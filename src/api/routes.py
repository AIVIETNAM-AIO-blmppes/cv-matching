import os
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, status
from src.etl.parser import DocumentParser
from src.api.schemas import MatchResponse
from src.etl.extractor import SemanticExtractor
import zipfile
import shutil
import tempfile
import uuid

router = APIRouter(prefix="/api/v1", tags=["Matching"])

ALLOWED_EXTENSIONS = {'.pdf', '.txt'}

import re
import spacy

nlp = spacy.load("en_core_web_md")

def extract_demographics(text: str) -> dict:
    # 1. Regex Patterns
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'
    
    # 2. Spacy NER
    doc = nlp(text[:10000]) # Only process the beginning of the CV for personal info
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Not found")
    location = next((ent.text for ent in doc.ents if ent.label_ == "GPE"), "Not found")
    
    return {
        "name": name,
        "email": re.search(email_pattern, text).group(0) if re.search(email_pattern, text) else "N/A",
        "phone": re.search(phone_pattern, text).group(0) if re.search(phone_pattern, text) else "N/A",
        "location": location
    }

@router.post("/evaluate", response_model=MatchResponse)
async def evaluate_cv(
    request: Request,
    cv_file: UploadFile = File(...),
    jd_skills: List[str] = Form(...)
):
    # 1. Kiểm tra ngoại lệ về định dạng file (Extension Validation)
    _, extension = os.path.splitext(cv_file.filename)
    if extension.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Định dạng file {extension} không được hỗ trợ. Hệ thống chỉ nhận file .pdf hoặc .txt"
        )

    # 2. Tạo thư mục tạm an toàn
    temp_dir = "data/raw/temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{cv_file.filename}")
    
    try:
        # Ghi dữ liệu file tạm
        with open(file_path, "wb") as f:
            content = await cv_file.read()
            # Kiểm tra xem file có bị trống hay không (Empty File validation)
            if len(content) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File tải lên trống rỗng (0 bytes). Vui lòng kiểm tra lại cấu trúc file."
                )
            f.write(content)
            
        # 3. Thực thi ETL Pipeline kết hợp bọc Exception xử lý file hỏng
        try:
            parsed_text = DocumentParser.extract_text(file_path)
            # print(parsed_text)
        except Exception as parser_err:
            # Bắt toàn bộ các lỗi liên quan đến file PDF hỏng cấu trúc từ tầng thư viện sâu
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File cấu trúc bị lỗi hoặc đã hỏng, không thể giải mã dữ liệu: {str(parser_err)}"
            )

        if not parsed_text or len(parsed_text.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nội dung file sau khi parse không đủ điều kiện phân tích (Văn bản quá ngắn hoặc lỗi bộ gõ)."
            )

        # 1. Get nouns only
        cv_nouns = SemanticExtractor.extract_nouns(parsed_text)
        
        # 2. Score via Matcher
        matcher = request.app.state.matcher
        candidate_id = f"CAND-{uuid.uuid4().hex[:6].upper()}"
        print(cv_nouns)
        score, details, matched_nouns = matcher.evaluate_candidate(cv_nouns, jd_skills, candidate_id)
        
        return MatchResponse(
            candidate_id=candidate_id,
            filename=cv_file.filename,
            match_score=score,
            extracted_skills=matched_nouns, # Now shows only the relevant matching nouns
            match_details=details
        )

    except HTTPException as http_ex:
        # Chuyển tiếp các HTTPException đã bắt ở trên ra ngoài
        raise http_ex
    except Exception as general_ex:
        # Bọc lỗi hệ thống không lường trước để server không crash sập
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống bất ngờ phát sinh: {str(general_ex)}"
        )
        
    finally:
        # Luôn luôn xóa file tạm giải phóng bộ nhớ kể cả khi có lỗi xảy ra
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/evaluate-batch")
async def evaluate_batch(
    request: Request,
    cv_zip: UploadFile = File(...),
    jd_skills: List[str] = Form(...)
):
    if not cv_zip.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên file .zip")

    # Tạo thư mục tạm để giải nén
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "uploaded.zip")
    extract_dir = os.path.join(temp_dir, "extracted")
    
    try:
        # Ghi file zip
        with open(zip_path, "wb") as f:
            f.write(await cv_zip.read())
            
        # Giải nén
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        results = []
        matcher = request.app.state.matcher
        
        # Duyệt qua các file đã giải nén
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(('.pdf', '.txt')):
                    file_path = os.path.join(root, file)
                    
                    try:
                        # 1. Parse nội dung
                        parsed_text = DocumentParser.extract_text(file_path)
                        if not parsed_text: continue
                        
                        # 2. Extract nouns (Sử dụng logic SemanticExtractor đã tối ưu)
                        cv_nouns = SemanticExtractor.extract_nouns(parsed_text)
                        
                        # 3. Chấm điểm
                        candidate_id = f"CAND-{uuid.uuid4().hex[:6].upper()}"
                        score, details, matched_nouns = matcher.evaluate_candidate(
                            cv_nouns, jd_skills, candidate_id
                        )
                        demographics = extract_demographics(parsed_text)
                        results.append({
                            "name": file,
                            "candidate_id": candidate_id,
                            "score": score,
                            "details": details,
                            "extracted_skills": matched_nouns,
                            "demographics": demographics
                        })
                    except Exception as e:
                        print(f"Lỗi xử lý file {file}: {str(e)}")
                        continue
        
        return results

    finally:
        # Xóa sạch thư mục tạm sau khi xử lý xong
        shutil.rmtree(temp_dir)
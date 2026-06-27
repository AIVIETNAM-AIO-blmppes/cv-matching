# BÁO CÁO KỸ THUẬT: HỆ THỐNG SMART-CV-MATCHING (SEMANTIC VERSION)

## 1. Đặt vấn đề (Problem Statement)
Trong bối cảnh tuyển dụng hiện đại, việc sàng lọc hồ sơ ứng viên đối mặt với ba rào cản lớn:
* **Khối lượng dữ liệu quá lớn:** Nhà tuyển dụng mất quá nhiều thời gian để sàng lọc thủ công.
* **Độ lệch ngữ nghĩa (Semantic Gap):** Các phương pháp so khớp từ khóa (keyword-based) truyền thống không hiểu được mối quan hệ ngữ nghĩa (ví dụ: "Python" và "Data Science" có liên quan).
* **Thiếu công cụ đối chiếu:** Sự thiếu hụt các công cụ đo lường độ khớp giữa bộ kỹ năng (skill set) trong CV và yêu cầu công việc (JD).

**Mục tiêu:** Xây dựng hệ thống tự động hóa sàng lọc ứng viên bằng trí tuệ nhân tạo, tập trung vào khả năng hiểu ngữ nghĩa và tính toán độ tương quan (Semantic Similarity) để hỗ trợ ra quyết định tuyển dụng.

---

## 2. Mô tả Dữ liệu (Data Description)
Hệ thống xử lý dữ liệu phi cấu trúc với quy trình cụ thể:
* **Đầu vào:** Tệp tin `.pdf` hoặc `.txt` nén trong file `.zip`.
* **Tiền xử lý (Pre-processing):**
    * **Document Parsing:** Chuyển đổi tệp tin sang văn bản thô.
    * **Semantic Extraction:** Sử dụng Spacy NLP để trích xuất thực thể (Entities) như: Tên ứng viên, Email, Số điện thoại, Địa điểm.
    * **Noun Extraction:** Sử dụng `SemanticExtractor` để tách lọc các danh từ chuyên môn (n-grams), tạo tập dữ liệu các "kỹ năng thô" phục vụ so khớp.

---

## 3. Phương pháp giải quyết (Solution & Logic)
Chúng tôi sử dụng mô hình **Vector Space Model (VSM)** kết hợp với **Symmetric Cosine Similarity** để đánh giá độ tương quan:

* **Vector Embedding:** Sử dụng mô hình `all-MiniLM-L6-v2` từ thư viện `sentence-transformers` để chuyển đổi các từ khóa kỹ năng (JD) và các danh từ chuyên môn (CV) thành các vector ngữ nghĩa trong không gian nhiều chiều.
* **Cosine Similarity Scoring:** Tính toán độ tương đồng cosine giữa vector kỹ năng của JD và danh sách kỹ năng của CV.
* **Symmetry Factor (Kiểm soát "ảo tưởng" dữ liệu):** Để tránh việc CV bị đánh giá cao do trích xuất nhầm từ khóa, hệ thống thực hiện kiểm tra 2 chiều (Reverse Similarity): 
    * Tính toán `(Noun -> Skill)` và `(Skill -> Noun)`.
    * Áp dụng `Symmetry Factor` (trung bình cộng của hai chiều) để loại bỏ các kết quả khớp một chiều (one-way hallucination), đảm bảo tính chính xác cho điểm số cuối cùng.
* **Điểm số cuối cùng:** Kết quả được chuẩn hóa về thang điểm phần trăm, dựa trên tổng điểm các kỹ năng yêu cầu (Weighted Scoring).

---

## 4. Kiến trúc hệ thống
### Kiến trúc tổng thể
Hệ thống được thiết kế theo kiến trúc Micro-service nhẹ:
* **Frontend:** SPA (Single Page Application) tương tác qua RESTful API.
* **Backend:** FastAPI với các service `SemanticExtractor` và `GraphMatcher` (Semantic Matcher) được tối ưu hóa để load vào bộ nhớ (RAM), đảm bảo thời gian phản hồi (latency) thấp nhất.

### Luồng hệ thống (Flowchart)
```mermaid
graph TD
    A[Người dùng tải CV ZIP + JD Skills] --> B{FastAPI Router}
    B --> C[ETL: Trích xuất Text]
    C --> D[SemanticExtractor: Lọc Nouns]
    D --> E[SentenceTransformer: Vectorize Nouns/Skills]
    E --> F[Tính toán Symmetric Cosine Similarity]
    F --> G[Xử lý Logic Điểm số]
    G --> H[Trả về Match Score + Details]
    H --> I[Ghi log metrics.json]
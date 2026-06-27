import os
import re
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Update this path if you are on Windows and installed Tesseract in a custom location.
# If on Mac/Linux, you can usually leave this commented out.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class DocumentParser:
    """
    Industrial-grade Document Parser.
    Uses PyMuPDF for layout-aware text extraction.
    Falls back to Tesseract OCR for scanned documents.
    """

    @staticmethod
    def _clean_raw_text(text: str) -> str:
        """Standardizes the text for the Graph Engine."""
        if not text:
            return ""
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip().lower()

    @staticmethod
    def _extract_text_pymupdf(file_path: str) -> str:
        """
        Extracts text using PyMuPDF. It groups text by blocks,
        which preserves 2-column CV layouts beautifully.
        """
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                # get_text("blocks") returns spatial text blocks
                blocks = page.get_text("blocks")
                # Sort blocks by vertical position (y0), then horizontal (x0) to read naturally
                blocks.sort(key=lambda b: (b[1], b[0]))
                
                for b in blocks:
                    if b[4].strip(): # b[4] contains the actual text string
                        text += b[4] + "\n"
            doc.close()
            return text
        except Exception as e:
            print(f"[Error] PyMuPDF failed on {file_path}: {e}")
            return ""

    @staticmethod
    def _extract_text_ocr(file_path: str) -> str:
        """
        OCR Fallback: Converts PDF pages to images and runs Tesseract.
        Heavy on CPU, only used when necessary.
        """
        print(f"[*] Text is empty or malformed. Triggering OCR Fallback for: {file_path}")
        text = ""
        try:
            # Convert PDF to a list of PIL Images (dpi=300 for good OCR accuracy)
            images = convert_from_path(file_path, dpi=300)
            for i, image in enumerate(images):
                # Using config '--psm 6' assumes a single uniform block of text. 
                # '--psm 4' is usually better for variable column sizes.
                page_text = pytesseract.image_to_string(image, config='--psm 4')
                text += page_text + "\n"
            return text
        except Exception as e:
            print(f"[Error] OCR failed on {file_path}: {e}")
            return ""

    @classmethod
    def parse_pdf(cls, file_path: str) -> str:
        """Smart PDF routing."""
        # 1. Try layout-aware extraction first
        raw_text = cls._extract_text_pymupdf(file_path)
        
        # 2. Check if the extraction looks like a scanned image 
        # (e.g., less than 50 characters found in the whole PDF)
        if len(raw_text.strip()) < 50:
            raw_text = cls._extract_text_ocr(file_path)
            
        return cls._clean_raw_text(raw_text)

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Basic TXT parsing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return DocumentParser._clean_raw_text(file.read())
        except Exception as e:
            print(f"[Error] TXT parsing failed {file_path}: {e}")
            return ""

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        The Main Router.
        """
        if not os.path.exists(file_path):
            print(f"[Error] File not found: {file_path}")
            return ""

        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == '.txt':
            return cls.parse_txt(file_path)
        elif extension == '.pdf':
            return cls.parse_pdf(file_path)
        else:
            print(f"[Warning] Unsupported file extension: {extension}")
            return ""
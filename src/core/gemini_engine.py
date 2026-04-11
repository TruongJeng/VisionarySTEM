"""
VisionarySTEM - Gemini 1.5 Pro Engine
========================================
Core AI engine that uses Gemini 1.5 Pro's native multimodal capabilities
to analyze STEM documents (PDFs/Images) and extract structured content.

Lõi AI sử dụng khả năng đa phương thức gốc của Gemini 1.5 Pro
để phân tích tài liệu STEM (PDF/Ảnh) và trích xuất nội dung có cấu trúc.
"""

import time
import json
import logging
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from src.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# ============================================
# Pydantic schema for Gemini structured output
# ============================================

class GeminiCoordinates(BaseModel):
    """Coordinates schema for Gemini response"""
    page: int = Field(description="Số trang (bắt đầu từ 1)")
    x: float = Field(description="Khoảng cách từ cạnh trái (%)")
    y: float = Field(description="Khoảng cách từ cạnh trên (%)")
    w: float = Field(description="Chiều rộng khối (%)")
    h: float = Field(description="Chiều cao khối (%)")
    region: str = Field(description="Vùng: top-left, top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right")


class GeminiContentBlock(BaseModel):
    """Single content block from Gemini analysis"""
    id: str = Field(description="Mã khối: block_001, block_002, ...")
    type: str = Field(description="Loại: text, math, chart, table, figure")
    raw_content: str = Field(description="Nội dung gốc được trích xuất")
    latex: Optional[str] = Field(default=None, description="Mã LaTeX (chỉ cho khối toán)")
    spoken_text: str = Field(description="Văn bản đọc tiếng Việt tự nhiên")
    confidence: float = Field(description="Điểm tin cậy 0.0 đến 1.0")
    coordinates: GeminiCoordinates


class GeminiAnalysisResult(BaseModel):
    """Complete analysis result from Gemini"""
    content_blocks: list[GeminiContentBlock]


# ============================================
# Gemini Engine Class
# ============================================

class GeminiEngine:
    """
    Wraps the Gemini 1.5 Pro API for STEM document analysis.
    Handles file upload, multimodal prompting, and structured JSON output.
    
    Bọc API Gemini 1.5 Pro cho phân tích tài liệu STEM.
    Xử lý upload file, prompt đa phương thức, và output JSON có cấu trúc.
    """

    def __init__(self):
        """Initialize the Gemini client with API key."""
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL
        logger.info(f"✅ GeminiEngine initialized with model: {self.model}")

    def analyze_document(
        self,
        file_path: str,
        page_number: int = 1,
        total_pages: int = 1,
    ) -> GeminiAnalysisResult:
        """
        Analyze a PDF or image file using Gemini 1.5 Pro.
        Returns structured content blocks with coordinates.
        
        Phân tích file PDF hoặc ảnh bằng Gemini 1.5 Pro.
        Trả về các khối nội dung có cấu trúc với tọa độ.
        
        Args:
            file_path: Path to the PDF or image file
            page_number: Current page being analyzed (for multi-page PDFs)
            total_pages: Total pages in the document
            
        Returns:
            GeminiAnalysisResult with content_blocks
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"📄 Uploading file: {file_path.name}")
        
        # Upload file via Gemini Files API
        uploaded_file = self.client.files.upload(file=str(file_path))
        
        # Wait for file processing
        max_wait = 30  # seconds
        waited = 0
        while uploaded_file.state.name == "PROCESSING" and waited < max_wait:
            time.sleep(2)
            waited += 2
            uploaded_file = self.client.files.get(name=uploaded_file.name)
            logger.info(f"⏳ File processing... ({waited}s)")
        
        if uploaded_file.state.name == "FAILED":
            raise RuntimeError(f"File upload failed: {uploaded_file.state.name}")
        
        logger.info(f"✅ File uploaded successfully: {uploaded_file.name}")
        
        # Build the analysis prompt
        analysis_prompt = f"""Phân tích trang {page_number}/{total_pages} của tài liệu STEM này.

Trích xuất TẤT CẢ các khối nội dung bạn nhìn thấy trên trang.
Với mỗi khối, cung cấp:
- id: đánh số tuần tự block_001, block_002, ...
- type: "text", "math", "chart", "table", hoặc "figure"
- raw_content: nội dung gốc
- latex: mã LaTeX (nếu là công thức toán, nếu không thì null)
- spoken_text: diễn giải bằng tiếng Việt TỰ NHIÊN (đặc biệt cho công thức toán)
- confidence: điểm tin cậy từ 0.0 đến 1.0
- coordinates: tọa độ theo phần trăm (x, y, w, h) và vùng (region)

LƯU Ý QUAN TRỌNG:
- Công thức toán PHẢI được đọc bằng tiếng Việt tự nhiên
  Ví dụ: "$F=ma$" → "Lực bằng khối lượng nhân gia tốc"
  Ví dụ: "$E=mc^2$" → "Năng lượng bằng khối lượng nhân bình phương tốc độ ánh sáng"
- Biểu đồ phải được mô tả chi tiết bằng tiếng Việt
- Tọa độ page phải là {page_number}"""

        # Call Gemini with structured output
        logger.info(f"🧠 Calling Gemini {self.model} for analysis...")
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                uploaded_file,
                analysis_prompt,
            ],
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=GeminiAnalysisResult,
                temperature=0.1,  # Low temperature for consistent, accurate output
            ),
        )
        
        # Parse the structured response
        result = response.parsed
        
        if result is None:
            # Fallback: try to parse from text
            logger.warning("⚠️ Parsed response is None, attempting manual JSON parse...")
            try:
                raw_json = json.loads(response.text)
                result = GeminiAnalysisResult(**raw_json)
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"❌ Failed to parse Gemini response: {e}")
                raise RuntimeError(f"Failed to parse Gemini response: {e}")
        
        logger.info(f"✅ Analysis complete: {len(result.content_blocks)} blocks found")
        
        # Cleanup: delete the uploaded file
        try:
            self.client.files.delete(name=uploaded_file.name)
            logger.info("🗑️ Uploaded file cleaned up")
        except Exception as e:
            logger.warning(f"⚠️ Could not delete uploaded file: {e}")
        
        return result

    def analyze_image_bytes(
        self,
        image_bytes: bytes,
        mime_type: str = "image/png",
        page_number: int = 1,
    ) -> GeminiAnalysisResult:
        """
        Analyze an image from bytes (for inline image analysis without file upload).
        Useful for extracting individual pages from PDFs as images.
        
        Phân tích ảnh từ bytes (phân tích ảnh nội tuyến không cần upload file).
        Hữu ích để trích xuất từng trang PDF dưới dạng ảnh.
        """
        analysis_prompt = f"""Phân tích trang tài liệu STEM này.

Trích xuất TẤT CẢ các khối nội dung bạn nhìn thấy.
Với mỗi khối, cung cấp id, type, raw_content, latex, spoken_text, confidence, và coordinates.

Công thức toán PHẢI được đọc bằng tiếng Việt tự nhiên.
Tọa độ page = {page_number}."""

        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                image_part,
                analysis_prompt,
            ],
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=GeminiAnalysisResult,
                temperature=0.1,
            ),
        )

        result = response.parsed
        if result is None:
            try:
                raw_json = json.loads(response.text)
                result = GeminiAnalysisResult(**raw_json)
            except Exception as e:
                raise RuntimeError(f"Failed to parse Gemini response: {e}")

        return result


# ============================================
# Module-level convenience function
# ============================================

_engine: Optional[GeminiEngine] = None

def get_engine() -> GeminiEngine:
    """
    Get or create a singleton GeminiEngine instance.
    Lấy hoặc tạo một instance GeminiEngine duy nhất.
    """
    global _engine
    if _engine is None:
        _engine = GeminiEngine()
    return _engine

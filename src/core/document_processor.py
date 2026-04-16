"""
VisionarySTEM - Document Processor
=====================================
Orchestrates the full document analysis pipeline:
PDF/Image → Gemini Analysis → Structured JSON → Spatial Index

Điều phối toàn bộ pipeline phân tích tài liệu:
PDF/Ảnh → Phân tích Gemini → JSON có cấu trúc → Chỉ mục không gian
"""

import time
import logging
from pathlib import Path
from collections import defaultdict

import fitz  # PyMuPDF

from src.config import GEMINI_MODEL
from src.core.gemini_engine import get_engine
from src.api.schemas import (
    ContentBlock,
    Coordinates,
    DocumentAnalysisResponse,
    DocumentMetadata,
    SpatialIndex,
)

logger = logging.getLogger(__name__)


def _get_page_count(file_path: Path) -> int:
    """Get the number of pages in a PDF file. Returns 1 for images."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        doc = fitz.open(str(file_path))
        count = doc.page_count
        doc.close()
        return count
    # Images are treated as single-page documents
    return 1


def _build_spatial_index(blocks: list[ContentBlock]) -> SpatialIndex:
    """
    Build a spatial index mapping regions to block IDs.
    Xây dựng chỉ mục không gian ánh xạ vùng đến mã khối.
    """
    regions: dict[str, list[str]] = defaultdict(list)
    for block in blocks:
        region = block.coordinates.region
        regions[region].append(block.id)
    return SpatialIndex(regions=dict(regions))


def _convert_gemini_to_schema(gemini_blocks, page_override: int = None) -> list[ContentBlock]:
    """
    Convert GeminiContentBlock objects to API schema ContentBlock objects.
    Chuyển đổi đối tượng GeminiContentBlock sang đối tượng ContentBlock schema API.
    """
    result = []
    for gb in gemini_blocks:
        # Clamp coordinates to 0-100 range (AI sometimes returns values slightly out of bounds)
        coords = Coordinates(
            page=page_override or gb.coordinates.page,
            x=max(0.0, min(100.0, gb.coordinates.x)),
            y=max(0.0, min(100.0, gb.coordinates.y)),
            w=max(0.0, min(100.0, gb.coordinates.w)),
            h=max(0.0, min(100.0, gb.coordinates.h)),
            region=gb.coordinates.region,
        )
        block = ContentBlock(
            id=gb.id,
            type=gb.type,
            raw_content=gb.raw_content,
            latex=gb.latex,
            spoken_text=gb.spoken_text,
            language="vi",
            confidence=gb.confidence,
            coordinates=coords,
        )
        result.append(block)
    return result


def analyze_file(file_path: str, filename: str = None) -> DocumentAnalysisResponse:
    """
    Full pipeline: Analyze a PDF or image file and return structured response.
    
    Pipeline đầy đủ: Phân tích file PDF hoặc ảnh và trả về phản hồi có cấu trúc.
    
    Args:
        file_path: Absolute path to the file
        filename: Original filename (for metadata)
        
    Returns:
        DocumentAnalysisResponse with all content blocks and spatial index
    """
    start_time = time.time()
    
    file_path = Path(file_path)
    if filename is None:
        filename = file_path.name
    
    logger.info(f"🔬 Starting analysis pipeline for: {filename}")
    
    # Get page count
    total_pages = _get_page_count(file_path)
    logger.info(f"📄 Document has {total_pages} page(s)")
    
    # Get the Gemini engine
    engine = get_engine()
    
    # Analyze the document
    all_blocks: list[ContentBlock] = []
    
    # Unified pipeline for both PDF and Images using PyMuPDF
    doc = fitz.open(str(file_path))
    try:
        for page_num in range(total_pages):
            logger.info(f"📄 Analyzing page {page_num + 1}/{total_pages}...")
            page = doc[page_num]
            
            # Render page to image (max 1500px to optimize latency)
            zoom = 1500.0 / max(page.rect.width, page.rect.height)
            if zoom > 2.5: 
                zoom = 2.5 # don't blow up small pages
                
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Compress as JPEG (quality 85) to reduce payload size
            # This cuts size from ~3MB (PNG 300DPI) to ~200KB, speeding up Gemini request
            img_bytes = pix.tobytes("jpeg", jpg_quality=85)
            
            logger.info(f"🖼️ Compressed image size: {len(img_bytes) // 1024} KB")
            
            gemini_result = engine.analyze_image_bytes(
                image_bytes=img_bytes,
                mime_type="image/jpeg",
                page_number=page_num + 1,
            )
            
            page_blocks = _convert_gemini_to_schema(
                gemini_result.content_blocks,
                page_override=page_num + 1,
            )
            
            # Re-number block IDs to be globally unique
            for i, block in enumerate(page_blocks):
                global_idx = len(all_blocks) + i + 1
                block.id = f"block_{global_idx:03d}"
            
            all_blocks.extend(page_blocks)
    finally:
        doc.close()
    
    # Calculate processing time
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    # Build spatial index
    spatial_index = _build_spatial_index(all_blocks)
    
    # Build final response
    response = DocumentAnalysisResponse(
        document_metadata=DocumentMetadata(
            filename=filename,
            total_pages=total_pages,
            processing_time_ms=processing_time_ms,
            model_used=GEMINI_MODEL,
        ),
        content_blocks=all_blocks,
        spatial_index=spatial_index,
    )
    
    logger.info(
        f"✅ Analysis complete: {len(all_blocks)} blocks, "
        f"{processing_time_ms}ms, "
        f"{len(spatial_index.regions)} regions"
    )
    
    return response

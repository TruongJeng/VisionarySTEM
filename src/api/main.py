"""
VisionarySTEM - FastAPI Application (Phase 2)
==============================================
REST API entry point for the VisionarySTEM backend.
Provides endpoints for document analysis, spatial queries, TTS audio, and health checks.

Điểm vào REST API cho backend VisionarySTEM.
Cung cấp endpoint phân tích tài liệu, truy vấn không gian, âm thanh TTS, và kiểm tra sức khỏe.
"""

import uuid
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.config import GEMINI_MODEL, MAX_FILE_SIZE_BYTES, UPLOAD_DIR, OUTPUT_DIR, print_config_summary
from src.api.schemas import (
    DocumentAnalysisResponse,
    HealthResponse,
    ErrorResponse,
    SpatialQueryRequest,
    SpatialQueryResponse,
    ContentBlock,
    Coordinates,
    DocumentMetadata,
    SpatialIndex,
)
from src.core.document_processor import analyze_file
from src.core.spatial_rag import get_rag_engine
from src.tts.edge_tts_engine import generate_speech_async

# ============================================
# Configure logging
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("VisionarySTEM")

# ============================================
# FastAPI Application
# ============================================
app = FastAPI(
    title="VisionarySTEM API",
    description=(
        "Multimodal AI Agent for Visually Impaired STEM Students\n\n"
        "Tro ly AI da phuong thuc cho sinh vien khiem thi khoi STEM.\n\n"
        "**Powered by Gemini 2.5 Flash** - Native Multimodal Analysis\n\n"
        "Phase 2: Spatial RAG + TTS Audio"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

# In-memory store: last analyzed document for quick query access
_last_analysis: dict = {}


# ============================================
# Startup Event
# ============================================
@app.on_event("startup")
async def startup_event():
    """Print config summary on startup"""
    print_config_summary()
    logger.info("VisionarySTEM API v2.0 is ready!")
    logger.info("API docs: http://localhost:8000/docs")


# ============================================
# SYSTEM ENDPOINTS
# ============================================

@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    summary="Health Check / Kiem tra suc khoe",
    tags=["System"],
)
async def health_check():
    """
    Check if the API is running and return service info.
    Kiem tra API co dang chay khong va tra ve thong tin dich vu.
    """
    return HealthResponse(
        status="ok",
        service="VisionarySTEM API",
        version="2.0.0",
        gemini_model=GEMINI_MODEL,
    )


# ============================================
# ANALYSIS ENDPOINTS
# ============================================

@app.post(
    "/api/v1/analyze",
    response_model=DocumentAnalysisResponse,
    summary="Analyze STEM Document / Phan tich tai lieu STEM",
    tags=["Analysis"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Analysis failed"},
    },
)
async def analyze_document(file: UploadFile = File(...)):
    """
    Upload a PDF or image file for STEM document analysis.
    Returns structured JSON with content blocks, coordinates, and spatial index.
    Automatically indexes results into Spatial RAG for voice queries.

    Tai len file PDF hoac anh de phan tich tai lieu STEM.
    Tra ve JSON co cau truc voi cac khoi noi dung, toa do, va chi muc khong gian.
    Tu dong lap chi muc ket qua vao Spatial RAG cho truy van giong noi.
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Save uploaded file temporarily
    unique_id = uuid.uuid4().hex[:8]
    safe_filename = f"{unique_id}_{file.filename}"
    temp_path = UPLOAD_DIR / safe_filename

    try:
        # Read and check file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_FILE_SIZE_BYTES // (1024*1024)} MB"
            )

        # Write to disk
        with open(temp_path, "wb") as f:
            f.write(content)

        logger.info(f"File saved: {temp_path} ({len(content)} bytes)")

        # Run analysis pipeline
        result = analyze_file(
            file_path=str(temp_path),
            filename=file.filename,
        )

        # Auto-index into Spatial RAG for voice queries
        doc_id = unique_id
        rag_engine = get_rag_engine()
        rag_engine.index_document(doc_id, result.content_blocks)

        # Store reference for subsequent queries
        _last_analysis["document_id"] = doc_id
        _last_analysis["response"] = result

        logger.info(f"Indexed into Spatial RAG: doc_id={doc_id}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        # Cleanup temp file (Windows-safe: file may still be locked by another process)
        try:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
                logger.info(f"Temp file cleaned up: {temp_path}")
        except PermissionError:
            logger.warning(f"Could not delete temp file (still locked): {temp_path}")


# ============================================
# SPATIAL QUERY ENDPOINTS
# ============================================

@app.post(
    "/api/v1/query",
    response_model=SpatialQueryResponse,
    summary="Spatial Voice Query / Truy van giong noi khong gian",
    tags=["Spatial Query"],
)
async def spatial_query(request: SpatialQueryRequest):
    """
    Process a natural language spatial query about a previously analyzed document.

    Xu ly truy van ngon ngu tu nhien ve khong gian cho tai lieu da phan tich.

    Example queries / Vi du truy van:
    - "Goc tren ben phai co gi?"
    - "Doc tat ca cong thuc toan"
    - "Bieu do o dau?"
    - "Phia duoi trang co noi dung gi?"
    """
    # Determine which document to query
    doc_id = request.document_id or _last_analysis.get("document_id")

    if not doc_id:
        raise HTTPException(
            status_code=400,
            detail="No document has been analyzed yet. Please upload a document first. / Chua co tai lieu nao duoc phan tich."
        )

    rag_engine = get_rag_engine()
    result = rag_engine.query(
        document_id=doc_id,
        query_text=request.query,
    )

    return result


# ============================================
# TTS (TEXT-TO-SPEECH) ENDPOINTS
# ============================================

@app.get(
    "/api/v1/tts/block/{block_id}",
    summary="Get Audio for Block / Lay audio cho khoi noi dung",
    tags=["TTS / Giong noi"],
    responses={
        200: {"content": {"audio/mpeg": {}}, "description": "MP3 audio file"},
        404: {"model": ErrorResponse, "description": "Block not found"},
    },
)
async def tts_block(block_id: str):
    """
    Generate and return TTS audio (MP3) for a specific content block.
    Uses the spoken_text from the last analyzed document.

    Tao va tra ve audio TTS (MP3) cho mot khoi noi dung cu the.
    Su dung spoken_text tu tai lieu duoc phan tich gan nhat.
    """
    last_resp = _last_analysis.get("response")
    if not last_resp:
        raise HTTPException(status_code=404, detail="No analysis available. Analyze a document first.")

    # Find the block
    target_block = None
    for block in last_resp.content_blocks:
        if block.id == block_id:
            target_block = block
            break

    if target_block is None:
        raise HTTPException(status_code=404, detail=f"Block {block_id} not found.")

    # Generate TTS
    audio_path = str(OUTPUT_DIR / f"tts_{block_id}.mp3")
    try:
        await generate_speech_async(target_block.spoken_text, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=f"{block_id}.mp3",
    )


@app.get(
    "/api/v1/tts/page/{page_number}",
    summary="Get Audio for Full Page / Lay audio cho toan trang",
    tags=["TTS / Giong noi"],
    responses={
        200: {"content": {"audio/mpeg": {}}, "description": "MP3 audio file"},
        404: {"model": ErrorResponse, "description": "Page not found"},
    },
)
async def tts_page(page_number: int = 1):
    """
    Generate and return full-page TTS audio by generating per-block and concatenating.

    Tao va tra ve audio TTS toan trang bang cach tao audio tung khoi roi noi lai.
    """
    last_resp = _last_analysis.get("response")
    if not last_resp:
        raise HTTPException(status_code=404, detail="No analysis available. Analyze a document first.")

    # Collect spoken_text for the requested page, ordered by y-coordinate (top to bottom)
    page_blocks = [
        b for b in last_resp.content_blocks
        if b.coordinates.page == page_number
    ]

    if not page_blocks:
        raise HTTPException(
            status_code=404,
            detail=f"No content found on page {page_number}."
        )

    # Sort top-to-bottom, left-to-right
    page_blocks.sort(key=lambda b: (b.coordinates.y, b.coordinates.x))

    # Generate per-block audio and concatenate MP3 bytes
    audio_path = str(OUTPUT_DIR / f"tts_page_{page_number}.mp3")
    combined_audio = b""

    for block in page_blocks:
        block_audio_path = str(OUTPUT_DIR / f"tts_tmp_{block.id}.mp3")
        try:
            await generate_speech_async(block.spoken_text, block_audio_path)
            with open(block_audio_path, "rb") as af:
                combined_audio += af.read()
            # Cleanup temp block audio
            Path(block_audio_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"TTS failed for {block.id}: {e}, skipping...")
            continue

    if not combined_audio:
        raise HTTPException(status_code=500, detail="TTS generation failed for all blocks.")

    with open(audio_path, "wb") as f:
        f.write(combined_audio)

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=f"page_{page_number}.mp3",
    )


@app.post(
    "/api/v1/tts/speak",
    summary="Speak Custom Text / Doc van ban tuy chinh",
    tags=["TTS / Giong noi"],
    responses={
        200: {"content": {"audio/mpeg": {}}, "description": "MP3 audio file"},
    },
)
async def tts_speak(text: str):
    """
    Generate TTS audio for any custom Vietnamese text.
    Useful for reading spatial query answers aloud.

    Tao audio TTS cho bat ky van ban tieng Viet tuy chinh nao.
    Huu ich de doc to cau tra loi truy van khong gian.
    """
    import hashlib
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    audio_path = str(OUTPUT_DIR / f"tts_custom_{text_hash}.mp3")

    try:
        await generate_speech_async(text, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=f"speech_{text_hash}.mp3",
    )


# ============================================
# MOCK ENDPOINT (For Person B Frontend Testing)
# ============================================

@app.get(
    "/api/v1/mock/analyze",
    response_model=DocumentAnalysisResponse,
    summary="Mock Analysis (For Frontend Testing) / Phan tich gia lap",
    tags=["Mock / Gia lap"],
)
async def mock_analyze():
    """
    Returns a mock analysis response for frontend development.
    Person B can use this to build the UI without a live Gemini connection.

    Tra ve phan hoi phan tich gia lap cho phat trien frontend.
    Nguoi B co the dung endpoint nay de xay giao dien ma khong can ket noi Gemini.
    """
    mock_response = DocumentAnalysisResponse(
        document_metadata=DocumentMetadata(
            filename="newton_law_sample.pdf",
            total_pages=1,
            processing_time_ms=1000,
            model_used="gemini-2.5-flash (mock)",
        ),
        content_blocks=[
            ContentBlock(
                id="block_001",
                type="text",
                raw_content="\u0110\u1ecbnh lu\u1eadt II Newton v\u1ec1 chuy\u1ec3n \u0111\u1ed9ng",
                latex=None,
                spoken_text="\u0110\u1ecbnh lu\u1eadt hai Niu-t\u01a1n v\u1ec1 chuy\u1ec3n \u0111\u1ed9ng.",
                language="vi",
                confidence=0.97,
                coordinates=Coordinates(
                    page=1, x=10, y=5, w=80, h=8, region="top-center"
                ),
            ),
            ContentBlock(
                id="block_002",
                type="text",
                raw_content="Gia t\u1ed1c c\u1ee7a m\u1ed9t v\u1eadt t\u1ec9 l\u1ec7 thu\u1eadn v\u1edbi l\u1ef1c t\u00e1c d\u1ee5ng l\u00ean n\u00f3 v\u00e0 t\u1ec9 l\u1ec7 ngh\u1ecbch v\u1edbi kh\u1ed1i l\u01b0\u1ee3ng c\u1ee7a n\u00f3.",
                latex=None,
                spoken_text="Gia t\u1ed1c c\u1ee7a m\u1ed9t v\u1eadt t\u1ec9 l\u1ec7 thu\u1eadn v\u1edbi l\u1ef1c t\u00e1c d\u1ee5ng l\u00ean n\u00f3 v\u00e0 t\u1ec9 l\u1ec7 ngh\u1ecbch v\u1edbi kh\u1ed1i l\u01b0\u1ee3ng c\u1ee7a n\u00f3.",
                language="vi",
                confidence=0.95,
                coordinates=Coordinates(
                    page=1, x=10, y=15, w=80, h=10, region="top-center"
                ),
            ),
            ContentBlock(
                id="block_003",
                type="math",
                raw_content="F = ma",
                latex="F = ma",
                spoken_text="L\u1ef1c b\u1eb1ng kh\u1ed1i l\u01b0\u1ee3ng nh\u00e2n gia t\u1ed1c.",
                language="vi",
                confidence=0.99,
                coordinates=Coordinates(
                    page=1, x=35, y=30, w=30, h=8, region="center"
                ),
            ),
            ContentBlock(
                id="block_004",
                type="math",
                raw_content="a = F/m",
                latex="a = \\frac{F}{m}",
                spoken_text="Gia t\u1ed1c b\u1eb1ng l\u1ef1c chia cho kh\u1ed1i l\u01b0\u1ee3ng.",
                language="vi",
                confidence=0.98,
                coordinates=Coordinates(
                    page=1, x=35, y=42, w=30, h=8, region="center"
                ),
            ),
            ContentBlock(
                id="block_005",
                type="chart",
                raw_content="[Bi\u1ec3u \u0111\u1ed3 \u0111\u01b0\u1eddng th\u1eb3ng: Tr\u1ee5c X - Gia t\u1ed1c (m/s\u00b2), Tr\u1ee5c Y - L\u1ef1c (N)]",
                latex=None,
                spoken_text="Bi\u1ec3u \u0111\u1ed3 \u0111\u01b0\u1eddng th\u1eb3ng th\u1ec3 hi\u1ec7n m\u1ed1i quan h\u1ec7 t\u1ec9 l\u1ec7 thu\u1eadn gi\u1eefa l\u1ef1c v\u00e0 gia t\u1ed1c. Tr\u1ee5c ho\u00e0nh l\u00e0 gia t\u1ed1c t\u00ednh b\u1eb1ng m\u00e9t tr\u00ean gi\u00e2y b\u00ecnh ph\u01b0\u01a1ng, tr\u1ee5c tung l\u00e0 l\u1ef1c t\u00ednh b\u1eb1ng Niu-t\u01a1n.",
                language="vi",
                confidence=0.92,
                coordinates=Coordinates(
                    page=1, x=15, y=55, w=70, h=35, region="bottom-center"
                ),
            ),
        ],
        spatial_index=SpatialIndex(
            regions={
                "top-center": ["block_001", "block_002"],
                "center": ["block_003", "block_004"],
                "bottom-center": ["block_005"],
            }
        ),
    )

    # Also index mock data into Spatial RAG so Person B can test /query
    rag_engine = get_rag_engine()
    rag_engine.index_document("mock_doc", mock_response.content_blocks)
    _last_analysis["document_id"] = "mock_doc"
    _last_analysis["response"] = mock_response

    return mock_response


# ============================================
# Run with: uvicorn src.api.main:app --reload
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

# VisionarySTEM - PROJECT STATE

> **Last Updated:** 2026-04-12
> **Current Phase:** Phase 2 (COMPLETED) -> Ready for Phase 3

---

## CURRENT STATUS

### Phase 1: Foundation - DONE
- Gemini 2.5 Flash engine with structured JSON output
- FastAPI with /health, /analyze, /mock/analyze
- Bilingual docs (EN/VI): README, API Contract, Architecture
- PyMuPDF PDF processing pipeline
- Edge TTS Vietnamese voice engine

### Phase 2: Spatial RAG + TTS Integration - DONE
- **Spatial RAG** (`src/core/spatial_rag.py`):
  - ChromaDB in-memory vector store
  - Vietnamese keyword-based region detection (9 regions)
  - Content type filtering (math, chart, table, figure, text)
  - Natural Vietnamese spoken answer generation
- **TTS API Endpoints**:
  - `/api/v1/tts/block/{block_id}` - Audio for single block
  - `/api/v1/tts/page/{page}` - Full page audio (per-block concat)
  - `/api/v1/tts/speak` - Custom text speech
- **Spatial Query Endpoint**:
  - `POST /api/v1/query` - Natural language spatial queries
  - Auto-indexes analysis results into ChromaDB
- **All 23/23 integration tests PASSED**

### Phase 3: Evaluation & Optimization - DONE
- **Latency Optimization** (`src/core/document_processor.py`):
  - PyMuPDF inline rendering (1500px, JPEG 85 compression).
  - Reduced payload size from ~3MB to ~150KB.
  - Bypassed intermediate Google Cloud Files Upload APIs in favor of High-Speed Inline Base64 Data API.
- **WER Benchmark System** (`src/evaluation/wer_calculator.py`):
  - `jiwer` Character Error Rate (CER) and WER analysis.
  - Robust bounding mapping using lowest CER indexing.
  - **Results**: Math WER = 0.0% (Perfect formulation).

### Tech Stack
- **AI Model:** Gemini 2.5 Flash (google-genai SDK)
- **Backend:** FastAPI v2.0.0
- **Frontend:** Streamlit (Person B)
- **TTS:** Edge TTS (vi-VN-HoaiMyNeural)
- **Vector DB:** ChromaDB (in-memory)
- **Evaluation:** Jiwer (WER/CER metrics)
- **API Key:** Managed in .env (gitignored)

---

## API ENDPOINTS (8 total)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/v1/health | Health check |
| POST | /api/v1/analyze | Real Gemini analysis + auto-index |
| POST | /api/v1/query | Spatial voice queries |
| GET | /api/v1/tts/block/{id} | Block audio |
| GET | /api/v1/tts/page/{page} | Full page audio |
| POST | /api/v1/tts/speak | Custom text speech |
| GET | /api/v1/mock/analyze | Mock data for Person B |

---

## NEXT STEPS (Phase 4: Frontend & Voice UI)

1. **Person B Integration**: Gửi tài liệu và phối hợp để Streamlit của Person B gọi `/api/v1/analyze` và `/api/v1/query`.
2. **Audio Playback**: Frontend phát trực tiếp audio từ Blob hoặc File Response của TTS.
3. **Competition Demo**: Dùng 1 PDF Thật (Đề cương Vật lý hoặc Vi tích phân) để quay Video Demo mượt mà từ Frontend tới Backend.
4. **Slide Presentation**: Hoàn thành Slide thuyết trình mô tả Core Engine và RAG.

---

> **Note for AI:** Read this file and `AI_RULES.md` first when resuming work.

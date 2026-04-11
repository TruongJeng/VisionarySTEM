# 🏗️ VisionarySTEM - System Architecture
# Kiến trúc Hệ thống VisionarySTEM

> TDTU Vibe Coding 2026

---

## High-Level Architecture / Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Visually Impaired Student)         │
│                        NGƯỜI DÙNG (Sinh viên khiếm thị)        │
│                                                                 │
│    📄 Upload PDF/Image          🎤 Voice Query                  │
│         ↓                           ↓                           │
├─────────────────────────────────────────────────────────────────┤
│                    FRONTEND (Person B - Streamlit)               │
│                    GIAO DIỆN (Người B - Streamlit)              │
│                                                                 │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│    │File      │  │PDF       │  │Audio     │  │Voice     │     │
│    │Upload    │  │Viewer    │  │Player  🔊│  │Recorder🎤│     │
│    └────┬─────┘  └──────────┘  └──────────┘  └────┬─────┘     │
│         │           REST API                       │            │
├─────────▼───────────────────────────────────────────▼────────────┤
│                    BACKEND (Person A - FastAPI)                  │
│                                                                 │
│    ┌────────────────────────────────────────────────────────┐   │
│    │                   API Layer (FastAPI)                   │   │
│    │  POST /analyze   GET /health   GET /mock/analyze       │   │
│    └────────┬────────────────────────────────┬──────────────┘   │
│             │                                │                  │
│    ┌────────▼────────┐            ┌──────────▼──────────┐      │
│    │ Document        │            │  Spatial RAG        │      │
│    │ Processor       │            │  (ChromaDB)         │      │
│    │ ┌──────────────┐│            │  - Region filtering │      │
│    │ │ PyMuPDF      ││            │  - Vector search    │      │
│    │ │ (PDF render) ││            │  - Voice query      │      │
│    │ └──────┬───────┘│            └─────────────────────┘      │
│    │        │        │                                          │
│    │ ┌──────▼───────┐│                                          │
│    │ │ Gemini 1.5   ││    ┌──────────────────────────┐         │
│    │ │ Pro Engine   ││    │  Edge TTS Engine          │         │
│    │ │ (Multimodal) ││    │  - Vietnamese voice       │         │
│    │ │              ││    │  - vi-VN-HoaiMyNeural     │         │
│    │ └──────────────┘│    └──────────────────────────┘         │
│    └─────────────────┘                                          │
│                                                                 │
│    ┌────────────────────────────────────────────────────────┐   │
│    │                  Evaluation Module                      │   │
│    │  - WER Calculator (jiwer)                              │   │
│    │  - Latency benchmarks                                  │   │
│    │  - Math accuracy metrics                               │   │
│    └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow / Luồng dữ liệu

```
1. User uploads PDF/Image
   Người dùng tải lên PDF/Ảnh
        │
        ▼
2. FastAPI receives file, validates type & size
   FastAPI nhận file, kiểm tra loại & kích thước
        │
        ▼
3. Document Processor extracts pages (PyMuPDF)
   Bộ xử lý tài liệu trích xuất trang (PyMuPDF)
        │
        ▼
4. Gemini 1.5 Pro analyzes multimodally:
   Gemini 1.5 Pro phân tích đa phương thức:
   - Text extraction / Trích xuất văn bản
   - Math → LaTeX / Toán → LaTeX
   - Chart description / Mô tả biểu đồ
   - Spatial coordinates / Tọa độ không gian
   - Vietnamese spoken text / Lời đọc tiếng Việt
        │
        ▼
5. Results returned as Structured JSON
   Kết quả trả về dạng JSON có cấu trúc
        │
        ├──→ Frontend renders content blocks
        │    Giao diện hiển thị các khối nội dung
        │
        ├──→ Spatial RAG indexes for voice queries
        │    Spatial RAG lập chỉ mục cho truy vấn giọng nói
        │
        └──→ Edge TTS generates Vietnamese audio
             Edge TTS tạo âm thanh tiếng Việt
```

---

## Security Architecture / Kiến trúc bảo mật

| Layer | Measure (EN) | Biện pháp (VI) |
|-------|-------------|-----------------|
| API Key | Stored in `.env`, loaded via `python-dotenv` | Lưu trong `.env`, tải qua `python-dotenv` |
| Git | `.gitignore` excludes `.env` and secrets | `.gitignore` loại trừ `.env` và bí mật |
| Upload | File type + size validation | Kiểm tra loại file + kích thước |
| CORS | Configurable allowed origins | Nguồn gốc được phép có thể cấu hình |
| Cleanup | Temp files deleted after processing | File tạm bị xóa sau khi xử lý |

---

*VisionarySTEM - Making STEM Accessible | Làm STEM Dễ tiếp cận*

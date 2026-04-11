# 🔬 VisionarySTEM

**Multimodal AI Agent for Visually Impaired STEM Students**
**Trợ lý AI Đa phương thức cho Sinh viên Khiếm thị khối STEM**

> TDTU Vibe Coding 2026 Competition Entry

---

## 🌟 Overview / Tổng quan

**English:**
VisionarySTEM is an AI-powered assistant that helps visually impaired students access STEM documents (PDFs, images). Using **Gemini 1.5 Pro's native multimodal capabilities**, it extracts text, mathematical formulas, charts, and spatial layout information from documents and converts them into natural Vietnamese speech.

**Tiếng Việt:**
VisionarySTEM là trợ lý AI giúp sinh viên khiếm thị tiếp cận tài liệu STEM (PDF, ảnh). Sử dụng **khả năng đa phương thức gốc của Gemini 1.5 Pro**, hệ thống trích xuất văn bản, công thức toán, biểu đồ và thông tin bố cục không gian từ tài liệu, chuyển đổi thành giọng đọc tiếng Việt tự nhiên.

---

## ✨ Key Features / Tính năng chính

| Feature | Description (EN) | Mô tả (VI) |
|---------|-----------------|-------------|
| 📄 PDF/Image Analysis | Direct multimodal analysis via Gemini 1.5 Pro | Phân tích đa phương thức trực tiếp qua Gemini 1.5 Pro |
| 🔢 Math Extraction | LaTeX extraction with natural Vietnamese reading | Trích xuất LaTeX với đọc tiếng Việt tự nhiên |
| 📊 Chart Description | Detailed Vietnamese descriptions of charts/graphs | Mô tả chi tiết biểu đồ bằng tiếng Việt |
| 🗺️ Spatial RAG | Location-based voice queries ("What's in the top right?") | Truy vấn giọng nói theo vị trí ("Góc trên bên phải có gì?") |
| 🔊 Text-to-Speech | Natural Vietnamese TTS via Edge TTS | Chuyển văn bản thành giọng nói Việt tự nhiên |
| 📈 WER Evaluation | Built-in accuracy measurement tools | Công cụ đo lường độ chính xác tích hợp |

---

## 🏗️ Architecture / Kiến trúc

```
PDF/Image → Gemini 1.5 Pro → Structured JSON → TTS (Vietnamese)
                  ↓
           Spatial RAG (ChromaDB)
                  ↓
          Voice Query Interface
```

**Tech Stack:**
- **AI Model:** Gemini 1.5 Pro (Native Multimodal)
- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit (Person B)
- **TTS:** Edge TTS (Vietnamese)
- **Spatial DB:** ChromaDB
- **Evaluation:** jiwer (WER)

---

## 🚀 Quick Start / Bắt đầu nhanh

### Prerequisites / Yêu cầu
- Python 3.10 - 3.12
- Gemini API Key ([Get one here](https://aistudio.google.com/apikey))

### Installation / Cài đặt

```bash
# 1. Clone the repository / Clone repo
git clone https://github.com/YOUR_TEAM/VisionarySTEM.git
cd VisionarySTEM

# 2. Create virtual environment / Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies / Cài đặt phụ thuộc
pip install -r requirements.txt

# 4. Configure environment / Cấu hình môi trường
copy .env.example .env
# Then edit .env and add your GEMINI_API_KEY
# Sau đó chỉnh .env và thêm GEMINI_API_KEY của bạn

# 5. Start the API server / Khởi chạy server API
uvicorn src.api.main:app --reload
```

### Verify Installation / Kiểm tra cài đặt

```bash
# Check health endpoint / Kiểm tra endpoint sức khỏe
curl http://localhost:8000/api/v1/health

# View API docs / Xem tài liệu API
# Open browser: http://localhost:8000/docs
```

---

## 📁 Project Structure / Cấu trúc dự án

```
VisionarySTEM/
├── .env                    # API keys (⚠️ DO NOT PUSH / KHÔNG PUSH)
├── .env.example            # Template for contributors
├── .gitignore
├── requirements.txt
├── README.md               # This file / File này
│
├── src/
│   ├── config.py           # Configuration loader
│   ├── core/
│   │   ├── gemini_engine.py      # 🧠 Gemini 1.5 Pro API
│   │   ├── document_processor.py # 📄 PDF/Image pipeline
│   │   ├── spatial_rag.py        # 🗺️ Spatial RAG (Phase 2)
│   │   └── math_handler.py       # 🔢 Math processing (Phase 2)
│   ├── tts/
│   │   └── edge_tts_engine.py    # 🔊 Text-to-Speech (Phase 2)
│   ├── evaluation/
│   │   └── wer_calculator.py     # 📈 WER evaluation
│   ├── api/
│   │   ├── main.py               # 🚀 FastAPI entry point
│   │   └── schemas.py            # 📋 Pydantic models (JSON Contract)
│   └── utils/
│       └── helpers.py
│
├── tests/
│   └── sample_data/              # Sample STEM documents
│
├── docs/
│   ├── api_contract.md           # 📋 API Contract for Person B
│   └── architecture.md           # 🏗️ System architecture
│
├── frontend/                     # 👤 Person B's Streamlit app
│   └── (Person B's workspace)
│
└── scripts/
    ├── demo.py                   # Quick demo
    └── run_benchmark.py          # WER & latency benchmarks
```

---

## 👥 Team Roles / Phân công

| Role | Responsibility (EN) | Trách nhiệm (VI) |
|------|---------------------|-------------------|
| **Person A** (Backend) | AI pipeline, Gemini API, Spatial RAG, FastAPI | Pipeline AI, API Gemini, Spatial RAG, FastAPI |
| **Person B** (Frontend) | Streamlit UI, Voice interface, Audio playback | Giao diện Streamlit, Giao diện giọng nói, Phát âm thanh |

### For Person B / Cho Người B:
1. Read `docs/api_contract.md` for the JSON contract / Đọc `docs/api_contract.md` để biết hợp đồng JSON
2. Use `/api/v1/mock/analyze` endpoint for development / Dùng endpoint `/api/v1/mock/analyze` để phát triển
3. Build your Streamlit app in the `frontend/` directory / Xây dựng app Streamlit trong thư mục `frontend/`

---

## 🔒 Security / Bảo mật

- ✅ API Key stored in `.env` (never pushed to GitHub)
- ✅ `.gitignore` configured to exclude secrets
- ✅ File upload validation (type + size limits)
- ✅ CORS configured for frontend access

---

## 📊 Evaluation Metrics / Chỉ số đánh giá

| Metric | Target | Mô tả |
|--------|--------|--------|
| WER (Text) | < 10% | Tỷ lệ lỗi từ cho văn bản |
| WER (Math) | < 5% | Tỷ lệ lỗi từ cho công thức toán |
| Latency | < 3s/page | Thời gian xử lý mỗi trang |
| Math Accuracy | > 95% | Độ chính xác LaTeX |

---

## 📝 License

MIT License - TDTU Vibe Coding 2026

---

*Built with ❤️ for accessibility | Xây dựng bằng ❤️ vì khả năng tiếp cận*

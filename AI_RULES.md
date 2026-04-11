# 🧬 VisionarySTEM - AI Core Rules (Quy tắc Bất biến)

> **Dành cho bất kỳ AI Assistant nào (Antigraviti, Claude, Gemini, v.v.) tiếp nhận dự án này.**
> **For any AI Assistant taking over this project.**

Mục tiêu của file này là lưu trữ "linh hồn" của dự án VisionarySTEM. Khi tiếp quản dự án, bạn **BẮT BUỘC** phải đọc và tuân thủ các quy tắc sau:

---

## 1. MỤC TIÊU CỐT LÕI (CORE GOAL)
- **Sứ mệnh**: Xây dựng Trợ lý AI đa phương thức (Multimodal AI Agent) hỗ trợ sinh viên khiếm thị học các môn Khoa học, Công nghệ, Kỹ thuật và Toán học (STEM).
- **Ưu tiên tối thượng**:
  - Độ chính xác toán học (Toán học phải được dịch chuẩn xác sang LaTeX và tiếng Việt tự nhiên).
  - Độ trễ (Latency) thấp nhất có thể. Đọc nội dung ngay khi phân tích xong (Streaming).
  - Trải nghiệm người dùng (UX) thông qua Voice Query (Truy vấn giọng nói theo không gian).

## 2. CÔNG NGHỆ CHÍNH (TECH STACK)
- **Mô hình AI Core**: Sử dụng **Gemini 2.5 Flash** (Native Multimodal) qua thư viện `google-genai`. **KHÔNG** dùng các API bên thứ 3 đắt đỏ như Mathpix hay Document AI.
- **Backend (Person A)**: FastAPI (Python). Xử lý RAG, AI routing.
- **Frontend (Person B)**: Streamlit (Python). Xử lý giao diện, hiển thị LaTeX, Voice Input/Output.
- **Xử lý tài liệu**: PyMuPDF (`fitz`), kết hợp với Gemini để xử lý trực tiếp ảnh/PDF.
- **Text-to-Speech (TTS)**: Edge TTS (Thư viện `edge-tts`) sử dụng giọng Tiếng Việt (`vi-VN-HoaiMyNeural`).
- **CSDL Vector (Mở rộng)**: ChromaDB (cho Spatial RAG).

## 3. HỢP ĐỒNG API (API CONTRACT)
- Bất kỳ thay đổi nào về Backend liên quan tới đầu ra đều **phải tuân thủ tuyệt đối chuẩn JSON Schema** định nghĩa tại `docs/api_contract.md`.
- Các trường bắt buộc cho mỗi content block: `id`, `type` (text, math, chart, figure, table), `raw_content`, `latex` (có thể null), `spoken_text` (100% tiếng Việt), và `coordinates` (page, x, y, w, h theo phần trăm %, kèm theo region).

## 4. QUY TẮC NGÔN NGỮ KHOA HỌC (LANGUAGE RULES)
- **Tài liệu dự án**: Tất cả tài liệu như README, kiến trúc, guide hướng dẫn **PHẢI** là Song ngữ (Tiếng Anh / Tiếng Việt).
- **Spoken Text (Giọng đọc)**: Phải 100% là tiếng Việt **Tự Nhiên**.
  - ❌ Sai: "F equals m times a"
  - ✅ Đúng: "Lực bằng khối lượng nhân gia tốc"

## 5. BẢO MẬT (SECURITY)
- Không bao giờ commit API Key lên GitHub.
- API Key luôn luôn được tải thông qua `src/config.py` đọc từ file `.env`.

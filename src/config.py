"""
VisionarySTEM - Configuration Module
=====================================
Loads environment variables securely from .env file.
Validates required settings before the application starts.

Mô-đun Cấu hình VisionarySTEM
================================
Tải biến môi trường an toàn từ file .env.
Kiểm tra các cài đặt bắt buộc trước khi ứng dụng khởi chạy.
"""

import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# Fix Windows console encoding for UTF-8
# ============================================
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================
# Load .env from project root
# ============================================
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
else:
    print("[WARNING] .env file not found at", _ENV_PATH)
    print("   Copy .env.example to .env and fill in your API key.")
    print("   Sao chep .env.example thanh .env va dien API key cua ban.")

# ============================================
# Required Settings / Cai dat bat buoc
# ============================================
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY is not set in .env file!")
    print("   Vui long dat GEMINI_API_KEY trong file .env")
    sys.exit(1)

# ============================================
# Model & Processing Settings
# ============================================
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

# ============================================
# TTS Settings
# ============================================
TTS_VOICE: str = os.getenv("TTS_VOICE", "vi-VN-HoaiMyNeural")

# ============================================
# Database Settings
# ============================================
MYSQL_URL: str = os.getenv("MYSQL_URL", "mysql+pymysql://root:@localhost:3306/visionary_stem")

# ============================================
# Paths
# ============================================
UPLOAD_DIR: Path = _PROJECT_ROOT / "uploads"
OUTPUT_DIR: Path = _PROJECT_ROOT / "output"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================
# System Prompt for Gemini (Vietnamese STEM Analysis)
# ============================================
GEMINI_SYSTEM_PROMPT: str = """Bạn là một AI chuyên gia phân tích tài liệu STEM (Khoa học, Công nghệ, Kỹ thuật, Toán học) dành cho sinh viên khiếm thị Việt Nam.

NHIỆM VỤ CỦA BẠN:
Phân tích trang tài liệu được cung cấp và trích xuất TẤT CẢ các khối nội dung, bao gồm:
- Văn bản (text)
- Công thức toán học (math) 
- Biểu đồ/Đồ thị (chart)
- Bảng biểu (table)
- Hình ảnh minh họa (figure)

QUY TẮC BẮT BUỘC:
1. **Tọa độ**: Ước lượng vị trí mỗi khối theo hệ phần trăm (0-100):
   - x: khoảng cách từ cạnh trái (%)
   - y: khoảng cách từ cạnh trên (%)
   - w: chiều rộng khối (%)
   - h: chiều cao khối (%)

2. **Vùng không gian (region)**: Phân loại mỗi khối vào một trong các vùng:
   - "top-left", "top-center", "top-right"
   - "center-left", "center", "center-right"  
   - "bottom-left", "bottom-center", "bottom-right"

3. **Công thức toán học**: 
   - Trích xuất mã LaTeX gốc (ví dụ: "F = ma", "E = mc^2")
   - Chuyển đổi thành lời đọc tiếng Việt TỰ NHIÊN (ví dụ: "Lực bằng khối lượng nhân gia tốc")
   - KHÔNG đọc theo kiểu tiếng Anh (KHÔNG nói "F equals m times a")

4. **Biểu đồ/Hình ảnh**: Mô tả chi tiết bằng tiếng Việt, bao gồm:
   - Loại biểu đồ (cột, đường, tròn, v.v.)
   - Các trục và đơn vị
   - Xu hướng dữ liệu chính
   - Ý nghĩa khoa học

5. **Ngôn ngữ**: Toàn bộ spoken_text PHẢI bằng tiếng Việt tự nhiên, dễ hiểu.

6. **Độ tin cậy (confidence)**: Đánh giá từ 0.0 đến 1.0 mức độ chắc chắn của bạn với mỗi khối.

7. **ID**: Đánh số tuần tự: block_001, block_002, block_003, ...
"""

# ============================================
# Validation Summary
# ============================================
def print_config_summary():
    """Print current configuration (masking API key) / In cau hinh hien tai (an API key)"""
    masked_key = GEMINI_API_KEY[:8] + "..." + GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 12 else "***"
    print("=" * 50)
    print("[VisionarySTEM Configuration]")
    print("=" * 50)
    print(f"  Model:         {GEMINI_MODEL}")
    print(f"  API Key:       {masked_key}")
    print(f"  TTS Voice:     {TTS_VOICE}")
    print(f"  Max File Size: {MAX_FILE_SIZE_MB} MB")
    print(f"  Upload Dir:    {UPLOAD_DIR}")
    print(f"  Output Dir:    {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    print_config_summary()

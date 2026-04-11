# 📋 VisionarySTEM API Contract
# Hợp đồng API VisionarySTEM

> **Version / Phiên bản:** 1.0.0
> **Last Updated / Cập nhật:** 2026-04-12
> **Status / Trạng thái:** ✅ ACTIVE - Person B can start building now!

---

## 🎯 Purpose / Mục đích

**English:**
This document defines the exact JSON data format that Person A's backend will send to Person B's frontend. Person B should use this contract to build the Streamlit UI **immediately** — no need to wait for the live backend.

**Tiếng Việt:**
Tài liệu này xác định chính xác định dạng dữ liệu JSON mà backend Người A sẽ gửi cho frontend Người B. Người B hãy dùng hợp đồng này để xây giao diện Streamlit **ngay lập tức** — không cần chờ backend hoàn thành.

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000
```

### Available Endpoints / Các endpoint khả dụng

| Method | Endpoint | Description (EN) | Mô tả (VI) | Status |
|--------|----------|-------------------|-------------|--------|
| `GET` | `/api/v1/health` | Health check | Kiểm tra sức khỏe | ✅ Ready |
| `POST` | `/api/v1/analyze` | Analyze PDF/Image | Phân tích PDF/Ảnh | ✅ Ready |
| `GET` | `/api/v1/mock/analyze` | Mock data (for frontend dev) | Dữ liệu giả lập (cho frontend) | ✅ Ready |

---

## 📊 JSON Response Schema / Cấu trúc JSON phản hồi

### Complete Response / Phản hồi đầy đủ

```json
{
  "document_metadata": {
    "filename": "newton_law_sample.pdf",
    "total_pages": 1,
    "processing_time_ms": 1000,
    "model_used": "gemini-1.5-pro"
  },
  "content_blocks": [
    {
      "id": "block_001",
      "type": "text",
      "raw_content": "Định luật II Newton về chuyển động",
      "latex": null,
      "spoken_text": "Định luật hai Niu-tơn về chuyển động.",
      "language": "vi",
      "confidence": 0.97,
      "coordinates": {
        "page": 1,
        "x": 10,
        "y": 5,
        "w": 80,
        "h": 8,
        "region": "top-center"
      }
    },
    {
      "id": "block_002",
      "type": "text",
      "raw_content": "Nội dung: Gia tốc của một vật tỉ lệ thuận với lực tác dụng lên nó và tỉ lệ nghịch với khối lượng của nó.",
      "latex": null,
      "spoken_text": "Nội dung: Gia tốc của một vật tỉ lệ thuận với lực tác dụng lên nó và tỉ lệ nghịch với khối lượng của nó.",
      "language": "vi",
      "confidence": 0.95,
      "coordinates": {
        "page": 1,
        "x": 10,
        "y": 15,
        "w": 80,
        "h": 10,
        "region": "top-center"
      }
    },
    {
      "id": "block_003",
      "type": "math",
      "raw_content": "F = ma",
      "latex": "F = ma",
      "spoken_text": "Lực bằng khối lượng nhân gia tốc.",
      "language": "vi",
      "confidence": 0.99,
      "coordinates": {
        "page": 1,
        "x": 35,
        "y": 30,
        "w": 30,
        "h": 8,
        "region": "center"
      }
    },
    {
      "id": "block_004",
      "type": "math",
      "raw_content": "a = F/m",
      "latex": "a = \\frac{F}{m}",
      "spoken_text": "Gia tốc bằng lực chia cho khối lượng.",
      "language": "vi",
      "confidence": 0.98,
      "coordinates": {
        "page": 1,
        "x": 35,
        "y": 42,
        "w": 30,
        "h": 8,
        "region": "center"
      }
    },
    {
      "id": "block_005",
      "type": "chart",
      "raw_content": "[Biểu đồ đường thẳng: Trục X - Gia tốc (m/s²), Trục Y - Lực (N)]",
      "latex": null,
      "spoken_text": "Biểu đồ đường thẳng thể hiện mối quan hệ tỉ lệ thuận giữa lực và gia tốc. Trục hoành là gia tốc tính bằng mét trên giây bình phương, trục tung là lực tính bằng Niu-tơn. Đường thẳng đi qua gốc tọa độ cho thấy khi gia tốc tăng thì lực cũng tăng tương ứng.",
      "language": "vi",
      "confidence": 0.92,
      "coordinates": {
        "page": 1,
        "x": 15,
        "y": 55,
        "w": 70,
        "h": 35,
        "region": "bottom-center"
      }
    }
  ],
  "spatial_index": {
    "regions": {
      "top-center": ["block_001", "block_002"],
      "center": ["block_003", "block_004"],
      "bottom-center": ["block_005"]
    }
  }
}
```

---

## 📐 Field Definitions / Định nghĩa các trường

### `document_metadata`

| Field | Type | Description (EN) | Mô tả (VI) |
|-------|------|-------------------|-------------|
| `filename` | `string` | Original uploaded filename | Tên file gốc đã tải lên |
| `total_pages` | `integer` | Number of pages processed | Số trang đã xử lý |
| `processing_time_ms` | `integer` | Processing time in milliseconds | Thời gian xử lý (mili giây) |
| `model_used` | `string` | AI model used for analysis | Model AI dùng để phân tích |

### `content_blocks[]`

| Field | Type | Description (EN) | Mô tả (VI) |
|-------|------|-------------------|-------------|
| `id` | `string` | Unique block ID (e.g., `block_001`) | Mã khối duy nhất |
| `type` | `enum` | `"text"`, `"math"`, `"chart"`, `"table"`, `"figure"` | Loại nội dung |
| `raw_content` | `string` | Original extracted content | Nội dung gốc được trích xuất |
| `latex` | `string?` | LaTeX code (null for non-math) | Mã LaTeX (null nếu không phải toán) |
| `spoken_text` | `string` | Natural Vietnamese speech | Lời đọc tiếng Việt tự nhiên |
| `language` | `string` | Language code (default: `"vi"`) | Mã ngôn ngữ (mặc định: `"vi"`) |
| `confidence` | `float` | AI confidence 0.0 - 1.0 | Độ tin cậy AI 0.0 - 1.0 |
| `coordinates` | `object` | Spatial position on page | Vị trí không gian trên trang |

### `coordinates`

| Field | Type | Range | Description (EN) | Mô tả (VI) |
|-------|------|-------|-------------------|-------------|
| `page` | `integer` | ≥ 1 | Page number | Số trang |
| `x` | `float` | 0-100 | Distance from left (%) | Khoảng cách từ trái (%) |
| `y` | `float` | 0-100 | Distance from top (%) | Khoảng cách từ trên (%) |
| `w` | `float` | 0-100 | Width (%) | Chiều rộng (%) |
| `h` | `float` | 0-100 | Height (%) | Chiều cao (%) |
| `region` | `string` | See below | Spatial region name | Tên vùng không gian |

### Spatial Regions / Vùng không gian

```
┌──────────┬──────────┬──────────┐
│ top-left │top-center│top-right │
├──────────┼──────────┼──────────┤
│center-   │  center  │ center-  │
│  left    │          │  right   │
├──────────┼──────────┼──────────┤
│ bottom-  │ bottom-  │ bottom-  │
│  left    │  center  │  right   │
└──────────┴──────────┴──────────┘
```

### `spatial_index`

| Field | Type | Description (EN) | Mô tả (VI) |
|-------|------|-------------------|-------------|
| `regions` | `object` | Map: region name → list of block IDs | Ánh xạ: tên vùng → danh sách mã khối |

---

## 🧪 How to Use Mock Data / Cách dùng dữ liệu giả lập

### Option 1: Call Mock Endpoint / Gọi endpoint giả lập

```python
import requests

# Just call this endpoint - no file upload needed!
# Chỉ cần gọi endpoint này - không cần upload file!
response = requests.get("http://localhost:8000/api/v1/mock/analyze")
data = response.json()

# Access content blocks / Truy cập khối nội dung
for block in data["content_blocks"]:
    print(f"[{block['type']}] {block['spoken_text']}")
```

### Option 2: Use Mock JSON File / Dùng file JSON giả lập

Save the JSON above as `mock_data.json` and load it in Streamlit:

```python
import json
import streamlit as st

# Load mock data / Tải dữ liệu giả lập
with open("mock_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Display / Hiển thị
st.title("VisionarySTEM")
for block in data["content_blocks"]:
    if block["type"] == "math":
        st.latex(block["latex"])
    st.write(f"🔊 {block['spoken_text']}")
```

### Option 3: Real Analysis / Phân tích thật

```python
import requests

# Upload a file for real Gemini analysis
# Tải file lên để phân tích bằng Gemini thật
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        files={"file": ("document.pdf", f, "application/pdf")}
    )

data = response.json()
```

---

## 🎨 Frontend Guidelines for Person B / Hướng dẫn Frontend cho Người B

### Recommended Streamlit Components / Các component Streamlit đề xuất

| Feature | Component | Purpose (EN) | Mục đích (VI) |
|---------|-----------|--------------|----------------|
| File Upload | `st.file_uploader()` | Accept PDF/Image | Nhận file PDF/Ảnh |
| LaTeX Display | `st.latex()` | Render math formulas | Hiển thị công thức toán |
| Audio Playback | `st.audio()` | Play TTS audio | Phát âm thanh TTS |
| Layout Viz | Custom HTML/CSS | Show block positions | Hiển thị vị trí các khối |
| Voice Input | `streamlit-mic-recorder` | Record voice queries | Thu âm truy vấn giọng nói |

### Suggested UI Layout / Bố cục giao diện đề xuất

```
┌─────────────────────────────────────────┐
│  🔬 VisionarySTEM                       │
├─────────────────┬───────────────────────┤
│                 │                       │
│   PDF Viewer    │   Analysis Results    │
│   (Upload area) │   - Content blocks    │
│                 │   - Spoken text       │
│                 │   - Play audio ▶️      │
│                 │                       │
├─────────────────┴───────────────────────┤
│  🎤 Voice Query: "Góc trên bên phải?"  │
│  🔊 Answer: "Có tiêu đề và công thức"   │
└─────────────────────────────────────────┘
```

### 🔄 Switching from Mock to Real / Chuyển từ giả lập sang thật

```python
import streamlit as st
import requests

# Toggle between mock and real / Chuyển đổi giữa giả lập và thật
USE_MOCK = st.sidebar.checkbox("Use Mock Data / Dùng dữ liệu giả lập", value=True)

if USE_MOCK:
    response = requests.get("http://localhost:8000/api/v1/mock/analyze")
else:
    uploaded_file = st.file_uploader("Upload PDF/Image")
    if uploaded_file:
        response = requests.post(
            "http://localhost:8000/api/v1/analyze",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        )

if response:
    data = response.json()
    # Render data... / Hiển thị dữ liệu...
```

---

## ⚠️ Important Notes / Lưu ý quan trọng

1. **All `spoken_text` is in Vietnamese** / Mọi `spoken_text` đều bằng tiếng Việt
2. **Coordinates are percentages (0-100)** / Tọa độ là phần trăm (0-100)
3. **`latex` field can be `null`** for non-math blocks / Trường `latex` có thể `null` cho khối không phải toán
4. **`confidence` ranges from 0.0 to 1.0** / `confidence` từ 0.0 đến 1.0
5. **Block IDs are globally unique** across pages / Mã khối duy nhất xuyên suốt các trang

---

## 📞 Contact / Liên hệ

Any questions about the API contract? Create a GitHub Issue or message Person A directly.
Có câu hỏi về hợp đồng API? Tạo GitHub Issue hoặc nhắn trực tiếp cho Người A.

---

*Last updated: 2026-04-12 | VisionarySTEM v1.0.0*

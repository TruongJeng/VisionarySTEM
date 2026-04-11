# Hướng dẫn Tích hợp dành cho Person B (Frontend - Streamlit)
Dự án: **VisionarySTEM** (Vibe Coding 2026)

Tài liệu này hướng dẫn cách kết nối giao diện của bạn với hệ thống Backend (AI & RAG) do Person A đã xây dựng.

---

## 1. Cấu hình Cơ bản

- **Base URL của Backend**: `http://localhost:8000`
- **Cách chạy Backend (nếu chưa chạy)**: Yêu cầu Person A gõ lệnh `uvicorn src.api.main:app --host 0.0.0.0 --port 8000` trên máy của họ.

Trong file Streamlit của bạn, hãy khai báo:
```python
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1"
```

---

## 2. API 1: Upload tài liệu & Phân tích (Analyze)

**Khi nào dùng?** Khi người dùng khiếm thị upload một file PDF hoặc ảnh.

**Cách gọi (Python `requests`):**
```python
# Upload file lên API
def analyze_document(file_bytes, filename):
    files = {"file": (filename, file_bytes)}
    response = requests.post(f"{API_BASE}/analyze", files=files)
    
    if response.status_code == 200:
        return response.json() # Trả về schema có "content_blocks"
    else:
        st.error("Lỗi phân tích!")
        return None
```

> 💡 **Mẹo cho UI**: Trạng thái chờ (`st.spinner`) có thể mất 15-20s. Bạn nên phát một âm thanh như "Đang quét tài liệu, vui lòng chờ..." để trải nghiệm tốt hơn.

---

## 3. API 2: Truy vấn Không gian bằng Giọng nói (Spatial Voice Query)

**Khi nào dùng?** Khi người dùng muốn tìm kiếm vị trí (Ví dụ: "Ở giữa có gì?").

**Cách gọi:**
```python
def query_spatial(question):
    payload = {"query": question}
    response = requests.post(f"{API_BASE}/query", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data["spoken_answer"] # Kéo trực tiếp câu trả lời bằng Tiếng Việt
    return "Xin lỗi, hệ thống chưa hiểu câu hỏi."
```

---

## 4. API 3: Phát âm thanh (Text-to-Speech)

Backend đã tích hợp AI tạo giọng nói Microsoft Edge TTS (giọng chuẩn Việt Nam).
Không cần viết hàm Python dài dòng, trong Streamlit bạn chỉ cần dùng URL trực tiếp vào thẻ `st.audio`.

1. **Đọc 1 khối văn bản cụ thể**:
```python
st.audio(f"{API_BASE}/tts/block/block_001", format="audio/mp3")
```

2. **Đọc cả 1 trang luôn**:
```python
st.audio(f"{API_BASE}/tts/page/1", format="audio/mp3")
```

3. **Bảo AI nói câu tùy ý** (Ví dụ kết quả của hàm `query_spatial` ở trên):
```python
spoken_answer = query_spatial("Góc trên phải có gì?")
response = requests.post(f"{API_BASE}/tts/speak", params={"text": spoken_answer})
st.audio(response.content, format="audio/mp3")
```

---

## 5. Mock API để Code Frontend khi không có mạng thật

Nếu bạn muốn test giao diện mà Server của Person A chưa chạy / không muốn tốn API quota:
Dùng API `/api/v1/mock/analyze` thay vì `/api/v1/analyze`. Kết quả trả về giống hệt 100% nhưng là dữ liệu fake (Định luật 2 Niu Tơn).

```python
response = requests.get(f"{API_BASE}/mock/analyze")
data = response.json()
blocks = data["content_blocks"]
```

---

## Bạn Cần Giao Giao Diện Như Thế Nào Cho Giám Khảo Xem?

1. **Giao diện cực kì đơn giản**: Chữ to, nút màu tương phản mạnh (Vì làm cho người khiếm thị / thị lực kém).
2. Tích hợp thư viện `audio_recorder_streamlit` hoặc HTML Voice Recorder để ghi âm thẳng trên trình duyệt.
3. Khi người dùng click vào nội dung nào trên màn hình -> Phát file âm thanh tương ứng!

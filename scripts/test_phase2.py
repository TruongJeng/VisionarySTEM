"""
Phase 2 Integration Test - Spatial RAG + TTS
=============================================
Tests all new Phase 2 endpoints in sequence.
"""
import httpx
import json
import time
import sys

BASE = "http://localhost:8000"
client = httpx.Client(timeout=120.0)

def test(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))
    return passed

results = []
print("=" * 60)
print(" VisionarySTEM Phase 2 - Integration Tests")
print("=" * 60)

# --- 1. Health Check ---
print("\n[1] Health Check")
r = client.get(f"{BASE}/api/v1/health")
data = r.json()
results.append(test("Status 200", r.status_code == 200))
results.append(test("Version 2.0.0", data.get("version") == "2.0.0", data.get("version")))

# --- 2. Mock Analyze (indexes into RAG) ---
print("\n[2] Mock Analyze + RAG Indexing")
r = client.get(f"{BASE}/api/v1/mock/analyze")
data = r.json()
results.append(test("Status 200", r.status_code == 200))
results.append(test("5 blocks returned", len(data["content_blocks"]) == 5, f"{len(data['content_blocks'])} blocks"))
results.append(test("Has spatial_index", "spatial_index" in data))
results.append(test("Model is mock", "mock" in data["document_metadata"]["model_used"]))

# --- 3. Spatial Query: Region-based ---
print("\n[3] Spatial Query - Region: 'center'")
r = client.post(f"{BASE}/api/v1/query", json={
    "query": "o giua trang co gi?",
})
data = r.json()
results.append(test("Status 200", r.status_code == 200))
results.append(test("Has matched_blocks", len(data["matched_blocks"]) > 0, f"{len(data['matched_blocks'])} matches"))
results.append(test("Has spoken_answer", len(data.get("spoken_answer", "")) > 0))
# Check that matched blocks are from center region
center_match = any(b["coordinates"]["region"] == "center" for b in data["matched_blocks"])
results.append(test("Matches include center region", center_match))

# --- 4. Spatial Query: Top area ---
print("\n[4] Spatial Query - Region: 'top/header'")
r = client.post(f"{BASE}/api/v1/query", json={
    "query": "phia tren trang co noi dung gi?",
})
data = r.json()
results.append(test("Status 200", r.status_code == 200))
results.append(test("Has matches", len(data["matched_blocks"]) > 0, f"{len(data['matched_blocks'])} matches"))

# --- 5. Spatial Query: Type filter (math) ---
print("\n[5] Spatial Query - Type: 'math/cong thuc'")
r = client.post(f"{BASE}/api/v1/query", json={
    "query": "doc tat ca cong thuc toan",
})
data = r.json()
results.append(test("Status 200", r.status_code == 200))
math_blocks = [b for b in data["matched_blocks"] if b["type"] == "math"]
results.append(test("Returns math blocks", len(math_blocks) > 0, f"{len(math_blocks)} math blocks"))

# --- 6. Spatial Query: Chart ---
print("\n[6] Spatial Query - Type: 'chart/bieu do'")
r = client.post(f"{BASE}/api/v1/query", json={
    "query": "bieu do o dau?",
})
data = r.json()
results.append(test("Status 200", r.status_code == 200))
chart_blocks = [b for b in data["matched_blocks"] if b["type"] == "chart"]
results.append(test("Returns chart block", len(chart_blocks) > 0, f"{len(chart_blocks)} chart blocks"))

# --- 7. TTS: Single block ---
print("\n[7] TTS - Single Block (block_003)")
r = client.get(f"{BASE}/api/v1/tts/block/block_003")
results.append(test("Status 200", r.status_code == 200))
results.append(test("Content-Type audio/mpeg", "audio" in r.headers.get("content-type", "")))
results.append(test("Audio size > 0", len(r.content) > 1000, f"{len(r.content)} bytes"))

# --- 8. TTS: Full page ---
print("\n[8] TTS - Full Page 1")
r = client.get(f"{BASE}/api/v1/tts/page/1")
results.append(test("Status 200", r.status_code == 200))
results.append(test("Audio size > 0", len(r.content) > 1000, f"{len(r.content)} bytes"))

# --- 9. TTS: Custom text ---
print("\n[9] TTS - Custom speak")
r = client.post(f"{BASE}/api/v1/tts/speak?text=Xin chao, day la VisionarySTEM")
results.append(test("Status 200", r.status_code == 200))
results.append(test("Audio size > 0", len(r.content) > 1000, f"{len(r.content)} bytes"))

# --- Summary ---
passed = sum(results)
total = len(results)
print("\n" + "=" * 60)
print(f" RESULTS: {passed}/{total} tests passed")
print("=" * 60)

if passed == total:
    print(" Phase 2 is FULLY OPERATIONAL!")
else:
    print(f" {total - passed} test(s) failed. Review above.")
    sys.exit(1)

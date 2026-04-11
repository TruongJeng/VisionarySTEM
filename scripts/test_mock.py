"""Quick test for the mock endpoint"""
import httpx
import json

r = httpx.get("http://localhost:8000/api/v1/mock/analyze")
data = r.json()

print("Status:", r.status_code)
print("Filename:", data["document_metadata"]["filename"])
print("Pages:", data["document_metadata"]["total_pages"])
print("Model:", data["document_metadata"]["model_used"])
print("Blocks:", len(data["content_blocks"]))
print()

for b in data["content_blocks"]:
    print(f"  {b['id']} [{b['type']}] confidence={b['confidence']}")
    print(f"    region: {b['coordinates']['region']}")
    print(f"    coords: x={b['coordinates']['x']}, y={b['coordinates']['y']}, w={b['coordinates']['w']}, h={b['coordinates']['h']}")
    print()

print("Spatial Index regions:", list(data["spatial_index"]["regions"].keys()))
print()

# Save to file for verification
with open("output/mock_verify.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Full JSON saved to output/mock_verify.json")

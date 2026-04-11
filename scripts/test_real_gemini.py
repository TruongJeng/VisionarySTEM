"""
Test real Gemini Analysis with sample PDF.
Test phan tich Gemini that voi PDF mau.
"""
import sys
import json
import time

sys.path.insert(0, ".")

print("=" * 60)
print("[VisionarySTEM] Testing REAL Gemini 1.5 Pro Analysis")
print("=" * 60)

# Test using the document processor directly (not via API)
from src.core.document_processor import analyze_file

pdf_path = "tests/sample_data/sample_physics.pdf"
print(f"\nFile: {pdf_path}")
print("Sending to Gemini 1.5 Pro... (may take 5-15 seconds)")
print()

start = time.time()

try:
    result = analyze_file(pdf_path, filename="sample_physics.pdf")
    elapsed = time.time() - start
    
    print(f"[OK] Analysis completed in {elapsed:.1f}s")
    print(f"[OK] Processing time (reported): {result.document_metadata.processing_time_ms}ms")
    print(f"[OK] Blocks found: {len(result.content_blocks)}")
    print()
    
    for block in result.content_blocks:
        print(f"  {block.id} [{block.type}]")
        print(f"    Raw: {block.raw_content[:80]}")
        if block.latex:
            print(f"    LaTeX: {block.latex}")
        print(f"    Spoken (VI): {block.spoken_text[:100]}")
        print(f"    Region: {block.coordinates.region}")
        print(f"    Confidence: {block.confidence:.0%}")
        print()
    
    # Save result
    result_dict = result.model_dump()
    output_path = "output/real_analysis_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    print(f"[SAVED] Full JSON: {output_path}")
    
    # Print spatial index
    print(f"\n[SPATIAL INDEX]")
    for region, ids in result.spatial_index.regions.items():
        print(f"  {region}: {', '.join(ids)}")
    
    print(f"\n{'=' * 60}")
    print(f"[SUCCESS] Gemini 1.5 Pro is working! API key is valid.")
    print(f"{'=' * 60}")

except Exception as e:
    elapsed = time.time() - start
    print(f"[ERROR] Analysis failed after {elapsed:.1f}s:")
    print(f"  {type(e).__name__}: {e}")
    print()
    print("Common fixes:")
    print("  1. Check your API key in .env")
    print("  2. Ensure you have Gemini 1.5 Pro access")
    print("  3. Check internet connection")
    import traceback
    traceback.print_exc()

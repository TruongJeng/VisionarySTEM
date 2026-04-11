"""
VisionarySTEM - Quick Demo Script
=====================================
Demonstrates the full analysis pipeline on a sample file.

Script demo nhanh - Minh họa pipeline phân tích hoàn chỉnh.

Usage / Cách dùng:
    python scripts/demo.py
    python scripts/demo.py --file path/to/document.pdf
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def run_demo(file_path: str = None):
    """Run a demonstration of the VisionarySTEM pipeline."""
    
    print("🔬 VisionarySTEM - Demo")
    print("=" * 60)
    
    # Print configuration
    from src.config import print_config_summary
    print_config_summary()
    
    if file_path is None:
        # Use mock data if no file provided
        print("\n📋 No file provided. Showing mock analysis result...")
        print("   (Use --file path/to/document.pdf to analyze a real file)\n")
        
        from src.api.main import mock_analyze
        import asyncio
        result = asyncio.run(mock_analyze())
        result_dict = result.model_dump()
    else:
        # Analyze the provided file
        print(f"\n📄 Analyzing: {file_path}")
        from src.core.document_processor import analyze_file
        result = analyze_file(file_path)
        result_dict = result.model_dump()
    
    # Pretty print the result
    print("\n" + "=" * 60)
    print("📊 Analysis Result / Kết quả phân tích:")
    print("=" * 60)
    
    meta = result_dict["document_metadata"]
    print(f"\n📁 File: {meta['filename']}")
    print(f"📄 Pages: {meta['total_pages']}")
    print(f"⏱️  Time: {meta['processing_time_ms']}ms")
    print(f"🤖 Model: {meta['model_used']}")
    
    print(f"\n📦 Content Blocks ({len(result_dict['content_blocks'])} found):")
    print("-" * 60)
    
    for block in result_dict["content_blocks"]:
        type_emoji = {
            "text": "📝",
            "math": "🔢",
            "chart": "📊",
            "table": "📋",
            "figure": "🖼️",
        }.get(block["type"], "📌")
        
        print(f"\n  {type_emoji} [{block['id']}] Type: {block['type']}")
        print(f"     Raw: {block['raw_content'][:80]}...")
        if block.get("latex"):
            print(f"     LaTeX: {block['latex']}")
        print(f"     🔊 Spoken: {block['spoken_text'][:100]}...")
        print(f"     📍 Position: ({block['coordinates']['x']:.0f}%, {block['coordinates']['y']:.0f}%) "
              f"Size: {block['coordinates']['w']:.0f}×{block['coordinates']['h']:.0f}% "
              f"Region: {block['coordinates']['region']}")
        print(f"     🎯 Confidence: {block['confidence']:.0%}")
    
    print(f"\n🗺️  Spatial Index:")
    for region, block_ids in result_dict["spatial_index"]["regions"].items():
        print(f"     {region}: {', '.join(block_ids)}")
    
    # Export full JSON
    output_path = Path(__file__).resolve().parent.parent / "output" / "demo_result.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Full JSON saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ Demo complete! / Demo hoàn tất!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VisionarySTEM Demo")
    parser.add_argument("--file", "-f", type=str, help="Path to PDF or image file")
    args = parser.parse_args()
    
    run_demo(args.file)

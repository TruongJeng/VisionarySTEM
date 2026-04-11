"""
VisionarySTEM - Benchmark Suite (Phase 3)
===========================================
Runs latency and accuracy (WER) tests against sample PDFs using Gemini Flash limit optimization.
"""

import os
import json
import time
from pathlib import Path
from pprint import pprint

from src.core.document_processor import analyze_file
from src.evaluation.wer_calculator import evaluate_document_accuracy

def run_benchmarks():
    print("=" * 60)
    print("🚀 VisionarySTEM Evaluation Benchmark (Phase 3)")
    print("=" * 60)
    
    # Locate test files
    project_root = Path(__file__).parent.parent
    sample_pdf = project_root / "tests" / "sample_data" / "sample_physics.pdf"
    gt_json_path = project_root / "tests" / "sample_data" / "benchmarks" / "sample_physics_gt.json"
    
    if not sample_pdf.exists() or not gt_json_path.exists():
        print(f"Error: Missing test files.")
        print(f"PDF exists: {sample_pdf.exists()}")
        print(f"GT exists: {gt_json_path.exists()}")
        return
        
    with open(gt_json_path, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
        
    print(f"📄 Testing PDF: {sample_pdf.name}")
    print(f"⏱️ Simulating request...")
    
    # 1. LATENCY BENCHMARK
    start_time = time.time()
    try:
        analysis_result = analyze_file(str(sample_pdf))
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    # 2. ACCURACY BENCHMARK (WER)
    accuracy_results = evaluate_document_accuracy(
        ground_truth_blocks=ground_truth,
        ai_generated_blocks=analysis_result.content_blocks
    )
    
    # Output to Console
    print("\n📊 BENCHMARK RESULTS")
    print("-" * 30)
    print(f"Độ trễ xử lý (Latency): {latency_ms/1000:.2f} s")
    print(f"Khối đã xử lý (Blocks): {len(analysis_result.content_blocks)} khối")
    
    overall = accuracy_results["overall"]
    print("\n🎯 ĐỘ CHÍNH XÁC (ACCURACY)")
    print(f"Lỗi văn bản tổng quát (Overall WER): {overall['wer']*100:.1f}%")
    print(f"Lỗi ký tự tổng quát (Overall CER): {overall['cer']*100:.1f}%")
    
    print("\nChi tiết theo loại nội dung:")
    for b_type, metrics in accuracy_results["by_type"].items():
        if metrics["count"] > 0:
            print(f" - {b_type.upper()}: WER = {metrics['wer']*100:.1f}%, CER = {metrics['cer']*100:.1f}% ({metrics['count']} blocks)")
            
    # Save Report
    report_path = project_root / "benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write(f"# VisionarySTEM Benchmark Report\n\n")
        rf.write(f"- **PDF**: `{sample_pdf.name}`\n")
        rf.write(f"- **Latency**: `{latency_ms/1000:.2f} s`\n")
        rf.write(f"- **Overall WER**: `{overall['wer']*100:.1f}%`\n")
        rf.write(f"- **Math WER**: `{accuracy_results['by_type'].get('math', {}).get('wer', 0.0)*100:.1f}%`\n")
        rf.write(f"\n> *Test được tự động sinh bởi VisionarySTEM Evaluation Script (Phase 3)*\n")
        
    print(f"\n✅ Đã lưu báo cáo tại: {report_path.name}")

if __name__ == "__main__":
    run_benchmarks()

import re
from typing import List, Dict, Tuple
import jiwer
import logging

logger = logging.getLogger(__name__)

def preprocess_vietnamese_text(text: str) -> str:
    """
    Standardize Vietnamese text for WER calculation:
    - Lowercase
    - Remove punctuation
    - Remove multiple spaces
    
    Chuẩn hóa văn bản Tiếng Việt để tính WER:
    - Chữ thường
    - Bỏ dấu câu
    - Bỏ khoảng trắng thừa
    """
    if not text:
        return ""
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_wer_cer(reference: str, hypothesis: str) -> Tuple[float, float]:
    """
    Calculate Word Error Rate (WER) and Character Error Rate (CER).
    Returns (wer, cer).
    
    Tính WER và CER.
    """
    ref_canon = preprocess_vietnamese_text(reference)
    hyp_canon = preprocess_vietnamese_text(hypothesis)
    
    if not ref_canon and not hyp_canon:
        return 0.0, 0.0
    if not ref_canon:
        return 1.0, 1.0
        
    try:
        wer = jiwer.wer(ref_canon, hyp_canon)
        cer = jiwer.cer(ref_canon, hyp_canon)
        return float(wer), float(cer)
    except ValueError as e:
        logger.warning(f"WER calculation failed: {e}. Ref: '{ref_canon}', Hyp: '{hyp_canon}'")
        return 1.0, 1.0

def evaluate_document_accuracy(
    ground_truth_blocks: List[Dict], 
    ai_generated_blocks: List[Dict]
) -> Dict:
    """
    Evaluate the accuracy of AI text generation against ground truth.
    Groups evaluation by type (text, math, etc.).
    
    Đánh giá độ chính xác của văn bản do AI sinh ra so với đáp án chuẩn.
    Nhóm đánh giá theo loại (văn bản, toán, v.v.).
    """
    results = {
        "overall": {"wer": 0.0, "cer": 0.0, "count": 0},
        "by_type": {}
    }
    
    total_wer = 0.0
    total_cer = 0.0
    count = 0
    
    # For robust benchmarking across different block orderings, 
    # we match each GT block to the AI block with the lowest CER.
    used_ai_indices = set()
    
    for gt_block in ground_truth_blocks:
        b_type = gt_block.get("type", "text")
        ref_text = gt_block.get("spoken_text", "")
        
        best_wer = 1.0
        best_cer = 1.0
        best_match_idx = -1
        
        for j, ai_block in enumerate(ai_generated_blocks):
            if j in used_ai_indices:
                continue
                
            hyp_text = ai_block.get("spoken_text", "") if isinstance(ai_block, dict) else ai_block.spoken_text
            wer, cer = calculate_wer_cer(ref_text, hyp_text)
            
            if cer < best_cer:
                best_cer = cer
                best_wer = wer
                best_match_idx = j
                
        if best_match_idx != -1:
            used_ai_indices.add(best_match_idx)
        else:
            # No AI block matched (e.g. AI returned fewer blocks)
            best_wer = 1.0
            best_cer = 1.0
        
        if b_type not in results["by_type"]:
            results["by_type"][b_type] = {"wer": 0.0, "cer": 0.0, "count": 0}
            
        results["by_type"][b_type]["wer"] += best_wer
        results["by_type"][b_type]["cer"] += best_cer
        results["by_type"][b_type]["count"] += 1
        
        total_wer += best_wer
        total_cer += best_cer
        count += 1
        
    if count > 0:
        results["overall"]["wer"] = total_wer / count
        results["overall"]["cer"] = total_cer / count
        results["overall"]["count"] = count
        
        for b_type in results["by_type"]:
            type_count = results["by_type"][b_type]["count"]
            if type_count > 0:
                results["by_type"][b_type]["wer"] /= type_count
                results["by_type"][b_type]["cer"] /= type_count
                
    return results

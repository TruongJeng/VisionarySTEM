"""
VisionarySTEM - Utility Helpers
=================================
Common utility functions used across the project.
Các hàm tiện ích chung dùng trong toàn dự án.
"""

import os
from pathlib import Path


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension / Lấy phần mở rộng file (chữ thường)"""
    return Path(filename).suffix.lower()


def is_supported_file(filename: str) -> bool:
    """
    Check if a file type is supported for analysis.
    Kiểm tra loại file có được hỗ trợ phân tích không.
    """
    supported = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    return get_file_extension(filename) in supported


def format_time_ms(ms: int) -> str:
    """
    Format milliseconds to human-readable string.
    Định dạng mili giây thành chuỗi dễ đọc.
    """
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    else:
        minutes = ms // 60000
        seconds = (ms % 60000) / 1000
        return f"{minutes}m {seconds:.0f}s"


def classify_region(x: float, y: float, w: float, h: float) -> str:
    """
    Classify a bounding box into one of 9 spatial regions.
    Phân loại hộp giới hạn vào một trong 9 vùng không gian.
    
    Uses the center point of the bounding box.
    Sử dụng điểm trung tâm của hộp giới hạn.
    """
    center_x = x + w / 2
    center_y = y + h / 2
    
    # Horizontal position
    if center_x < 33.3:
        h_pos = "left"
    elif center_x < 66.6:
        h_pos = "center"
    else:
        h_pos = "right"
    
    # Vertical position
    if center_y < 33.3:
        v_pos = "top"
    elif center_y < 66.6:
        v_pos = "center"
    else:
        v_pos = "bottom"
    
    # Combine  
    if v_pos == "center" and h_pos == "center":
        return "center"
    elif v_pos == "center":
        return f"center-{h_pos}"
    elif h_pos == "center":
        return f"{v_pos}-center"
    else:
        return f"{v_pos}-{h_pos}"

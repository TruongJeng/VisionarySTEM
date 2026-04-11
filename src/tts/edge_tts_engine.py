"""
VisionarySTEM - Edge TTS Engine
==================================
Text-to-Speech engine using Microsoft Edge TTS.
Generates natural Vietnamese speech from spoken_text.

Bộ chuyển văn bản thành giọng nói sử dụng Microsoft Edge TTS.
Tạo giọng đọc tiếng Việt tự nhiên từ spoken_text.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import edge_tts

from src.config import TTS_VOICE, OUTPUT_DIR

logger = logging.getLogger(__name__)


async def generate_speech_async(
    text: str,
    output_path: Optional[str] = None,
    voice: str = TTS_VOICE,
) -> str:
    """
    Generate speech audio from text using Edge TTS (async).
    Tạo âm thanh giọng nói từ văn bản bằng Edge TTS (bất đồng bộ).
    
    Args:
        text: Vietnamese text to speak / Văn bản tiếng Việt cần đọc
        output_path: Path to save audio file / Đường dẫn lưu file âm thanh
        voice: TTS voice name / Tên giọng đọc TTS
        
    Returns:
        Path to the generated audio file / Đường dẫn đến file âm thanh đã tạo
    """
    if output_path is None:
        # Generate unique filename
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        output_path = str(OUTPUT_DIR / f"tts_{text_hash}.mp3")
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    
    logger.info(f"🔊 TTS generated: {output_path}")
    return output_path


def generate_speech(
    text: str,
    output_path: Optional[str] = None,
    voice: str = TTS_VOICE,
) -> str:
    """
    Synchronous wrapper for generate_speech_async.
    Bọc đồng bộ cho generate_speech_async.
    """
    return asyncio.run(generate_speech_async(text, output_path, voice))


async def generate_block_audio(
    blocks: list[dict],
    output_dir: Optional[str] = None,
    voice: str = TTS_VOICE,
) -> list[dict]:
    """
    Generate audio for all content blocks.
    Tạo âm thanh cho tất cả các khối nội dung.
    
    Args:
        blocks: List of content block dicts with 'spoken_text' and 'id'
        output_dir: Directory to save audio files
        voice: TTS voice name
        
    Returns:
        List of dicts with 'block_id' and 'audio_path'
    """
    if output_dir is None:
        output_dir = str(OUTPUT_DIR)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = []
    for block in blocks:
        block_id = block.get("id", "unknown")
        spoken_text = block.get("spoken_text", "")
        
        if not spoken_text:
            continue
        
        audio_path = str(Path(output_dir) / f"{block_id}.mp3")
        
        try:
            await generate_speech_async(spoken_text, audio_path, voice)
            results.append({
                "block_id": block_id,
                "audio_path": audio_path,
            })
        except Exception as e:
            logger.error(f"❌ TTS failed for {block_id}: {e}")
    
    return results


# ============================================
# CLI Demo
# ============================================
if __name__ == "__main__":
    print("🔊 VisionarySTEM TTS Engine Demo")
    print("=" * 50)
    
    test_texts = [
        "Định luật hai Niu-tơn về chuyển động.",
        "Lực bằng khối lượng nhân gia tốc.",
        "Năng lượng bằng khối lượng nhân bình phương tốc độ ánh sáng.",
    ]
    
    for i, text in enumerate(test_texts):
        output = generate_speech(text, str(OUTPUT_DIR / f"demo_{i+1}.mp3"))
        print(f"  ✅ Generated: {output}")
    
    print("\n🎉 Demo complete! Check the output/ directory for audio files.")

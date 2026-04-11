"""
VisionarySTEM - Spatial RAG Engine (Phase 2)
================================================
Retrieval-Augmented Generation with spatial awareness.
Allows voice queries like "What's in the top right corner?"

Công cụ RAG có nhận thức không gian.
Cho phép truy vấn giọng nói như "Góc trên bên phải có gì?"
"""

import logging
import uuid
from typing import Optional
from collections import defaultdict

import chromadb
from chromadb.config import Settings

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.api.schemas import ContentBlock, Coordinates, SpatialQueryResponse

logger = logging.getLogger(__name__)

# ============================================
# Region keyword mapping for Vietnamese queries
# Ánh xạ từ khóa vùng cho truy vấn tiếng Việt
# ============================================
REGION_KEYWORDS: dict[str, list[str]] = {
    "top-left": [
        "góc trên bên trái", "trên trái", "phía trên bên trái",
        "top left", "upper left",
    ],
    "top-center": [
        "phía trên", "trên cùng", "đầu trang", "tiêu đề",
        "top center", "top", "header",
    ],
    "top-right": [
        "góc trên bên phải", "trên phải", "phía trên bên phải",
        "top right", "upper right",
    ],
    "center-left": [
        "bên trái", "giữa bên trái", "phía trái",
        "center left", "left side",
    ],
    "center": [
        "ở giữa", "chính giữa", "trung tâm", "giữa trang",
        "center", "middle",
    ],
    "center-right": [
        "bên phải", "giữa bên phải", "phía phải",
        "center right", "right side",
    ],
    "bottom-left": [
        "góc dưới bên trái", "dưới trái", "phía dưới bên trái",
        "bottom left", "lower left",
    ],
    "bottom-center": [
        "phía dưới", "dưới cùng", "cuối trang", "chân trang",
        "bottom center", "bottom", "footer",
    ],
    "bottom-right": [
        "góc dưới bên phải", "dưới phải", "phía dưới bên phải",
        "bottom right", "lower right",
    ],
}

# Type keywords for filtering / Từ khóa loại cho lọc
TYPE_KEYWORDS: dict[str, list[str]] = {
    "math": [
        "công thức", "toán", "phương trình", "math", "formula", "equation",
        "latex",
    ],
    "chart": [
        "biểu đồ", "đồ thị", "chart", "graph", "plot",
    ],
    "table": [
        "bảng", "table",
    ],
    "figure": [
        "hình", "ảnh", "figure", "image", "picture",
    ],
    "text": [
        "văn bản", "chữ", "nội dung", "text", "paragraph",
    ],
}

# Spatial relationship keywords / Từ khóa quan hệ không gian
RELATION_KEYWORDS: dict[str, list[str]] = {
    "above": ["trên", "phía trên", "bên trên", "above", "over"],
    "below": ["dưới", "phía dưới", "bên dưới", "below", "under", "beneath"],
    "left_of": ["trái", "bên trái", "left of"],
    "right_of": ["phải", "bên phải", "right of"],
    "next_to": ["cạnh", "bên cạnh", "kế bên", "next to", "beside"],
}


class SpatialRAGEngine:
    """
    Spatial RAG engine using ChromaDB for vector storage and
    keyword-based region matching for spatial queries.

    Công cụ RAG không gian sử dụng ChromaDB cho lưu trữ vector
    và đối khớp vùng dựa trên từ khóa cho truy vấn không gian.
    """

    def __init__(self):
        """Initialize ChromaDB client (in-memory for competition speed)."""
        self._client = chromadb.Client(Settings(
            anonymized_telemetry=False,
        ))
        self._collections: dict[str, chromadb.Collection] = {}
        logger.info("[SpatialRAG] Engine initialized (in-memory ChromaDB)")

    def index_document(
        self,
        document_id: str,
        content_blocks: list[ContentBlock],
    ) -> str:
        """
        Index content blocks from a document analysis into ChromaDB.
        Lập chỉ mục các khối nội dung từ phân tích tài liệu vào ChromaDB.

        Args:
            document_id: Unique ID for this document session
            content_blocks: List of ContentBlock from analysis

        Returns:
            document_id used for later queries
        """
        # Create or get collection for this document
        collection_name = f"doc_{document_id.replace('-', '_')[:50]}"

        # Delete existing if re-indexing
        try:
            self._client.delete_collection(collection_name)
        except Exception:
            pass

        collection = self._client.create_collection(
            name=collection_name,
            metadata={"document_id": document_id},
        )

        ids = []
        documents = []
        metadatas = []

        for block in content_blocks:
            # Build a rich text document for semantic search
            doc_text = f"{block.spoken_text} {block.raw_content}"
            if block.latex:
                doc_text += f" LaTeX: {block.latex}"

            ids.append(block.id)
            documents.append(doc_text)
            metadatas.append({
                "block_id": block.id,
                "type": block.type,
                "raw_content": block.raw_content,
                "latex": block.latex or "",
                "spoken_text": block.spoken_text,
                "language": block.language,
                "confidence": block.confidence,
                "page": block.coordinates.page,
                "x": block.coordinates.x,
                "y": block.coordinates.y,
                "w": block.coordinates.w,
                "h": block.coordinates.h,
                "region": block.coordinates.region,
            })

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        self._collections[document_id] = collection
        logger.info(
            f"[SpatialRAG] Indexed {len(ids)} blocks for document {document_id}"
        )
        return document_id

    def query(
        self,
        document_id: str,
        query_text: str,
        top_k: int = 5,
    ) -> SpatialQueryResponse:
        """
        Process a natural language spatial query against indexed document.
        Xử lý truy vấn ngôn ngữ tự nhiên về không gian cho tài liệu đã lập chỉ mục.

        Examples / Ví dụ:
            "Góc trên bên phải có gì?"
            "Công thức ở giữa trang là gì?"
            "Dưới biểu đồ có gì?"
            "Đọc tất cả công thức toán"
        """
        collection = self._collections.get(document_id)
        if collection is None:
            return SpatialQueryResponse(
                query=query_text,
                matched_blocks=[],
                spoken_answer="Không tìm thấy tài liệu. Vui lòng tải lên và phân tích tài liệu trước.",
            )

        query_lower = query_text.lower()

        # --- Step 1: Detect target regions from query ---
        target_regions = self._detect_regions(query_lower)

        # --- Step 2: Detect target content types ---
        target_types = self._detect_types(query_lower)

        # --- Step 3: Build ChromaDB filter ---
        where_filter = self._build_filter(target_regions, target_types)

        # --- Step 4: Query ChromaDB ---
        try:
            if where_filter:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                    where=where_filter,
                )
            else:
                # Pure semantic search (no spatial/type filter)
                results = collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                )
        except Exception as e:
            logger.error(f"[SpatialRAG] Query failed: {e}")
            # Fallback to unfiltered query
            results = collection.query(
                query_texts=[query_text],
                n_results=top_k,
            )

        # --- Step 5: Convert results to ContentBlock list ---
        matched_blocks = self._results_to_blocks(results)

        # --- Step 6: Generate spoken answer ---
        spoken_answer = self._generate_spoken_answer(
            query_text, matched_blocks, target_regions, target_types
        )

        return SpatialQueryResponse(
            query=query_text,
            matched_blocks=matched_blocks,
            spoken_answer=spoken_answer,
        )

    # ============================================
    # Private helpers
    # ============================================

    def _detect_regions(self, query_lower: str) -> list[str]:
        """Detect spatial regions mentioned in the query."""
        found = []
        for region, keywords in REGION_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    found.append(region)
                    break
        return found

    def _detect_types(self, query_lower: str) -> list[str]:
        """Detect content types mentioned in the query."""
        found = []
        for ctype, keywords in TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    found.append(ctype)
                    break
        return found

    def _build_filter(
        self,
        regions: list[str],
        types: list[str],
    ) -> Optional[dict]:
        """Build a ChromaDB where-filter from detected regions and types."""
        conditions = []

        if regions:
            if len(regions) == 1:
                conditions.append({"region": {"$eq": regions[0]}})
            else:
                conditions.append({"$or": [{"region": {"$eq": r}} for r in regions]})

        if types:
            if len(types) == 1:
                conditions.append({"type": {"$eq": types[0]}})
            else:
                conditions.append({"$or": [{"type": {"$eq": t}} for t in types]})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    def _results_to_blocks(self, results: dict) -> list[ContentBlock]:
        """Convert ChromaDB query results to ContentBlock objects."""
        blocks = []
        if not results or not results.get("metadatas"):
            return blocks

        for metadata_list in results["metadatas"]:
            for meta in metadata_list:
                try:
                    block = ContentBlock(
                        id=meta["block_id"],
                        type=meta["type"],
                        raw_content=meta["raw_content"],
                        latex=meta["latex"] if meta.get("latex") else None,
                        spoken_text=meta["spoken_text"],
                        language=meta.get("language", "vi"),
                        confidence=meta.get("confidence", 0.9),
                        coordinates=Coordinates(
                            page=meta["page"],
                            x=meta["x"],
                            y=meta["y"],
                            w=meta["w"],
                            h=meta["h"],
                            region=meta["region"],
                        ),
                    )
                    blocks.append(block)
                except Exception as e:
                    logger.warning(f"[SpatialRAG] Skipping malformed result: {e}")
        return blocks

    def _generate_spoken_answer(
        self,
        query: str,
        blocks: list[ContentBlock],
        regions: list[str],
        types: list[str],
    ) -> str:
        """Generate a natural Vietnamese spoken answer from matched blocks."""
        if not blocks:
            if regions:
                region_names = ", ".join(regions)
                return f"Không tìm thấy nội dung nào ở vùng {region_names}."
            return "Không tìm thấy nội dung phù hợp với câu hỏi của bạn."

        # Build context-aware answer
        parts = []

        if regions:
            region_vi = {
                "top-left": "góc trên bên trái",
                "top-center": "phía trên",
                "top-right": "góc trên bên phải",
                "center-left": "bên trái",
                "center": "ở giữa",
                "center-right": "bên phải",
                "bottom-left": "góc dưới bên trái",
                "bottom-center": "phía dưới",
                "bottom-right": "góc dưới bên phải",
            }
            region_desc = ", ".join(
                region_vi.get(r, r) for r in regions
            )
            parts.append(f"Tại vùng {region_desc}, tôi tìm thấy {len(blocks)} nội dung.")
        else:
            parts.append(f"Tôi tìm thấy {len(blocks)} nội dung liên quan.")

        # Describe each block
        for i, block in enumerate(blocks, 1):
            type_vi = {
                "text": "Văn bản",
                "math": "Công thức toán",
                "chart": "Biểu đồ",
                "table": "Bảng",
                "figure": "Hình ảnh",
            }.get(block.type, block.type)

            parts.append(f"Thứ {i}: {type_vi}. {block.spoken_text}")

        return " ".join(parts)

    def get_all_documents(self) -> list[str]:
        """Return list of indexed document IDs."""
        return list(self._collections.keys())

    def delete_document(self, document_id: str) -> bool:
        """Remove a document from the index."""
        collection = self._collections.pop(document_id, None)
        if collection:
            try:
                self._client.delete_collection(collection.name)
            except Exception:
                pass
            return True
        return False


# ============================================
# Singleton accessor
# ============================================
_rag_engine: Optional[SpatialRAGEngine] = None


def get_rag_engine() -> SpatialRAGEngine:
    """Get or create the singleton SpatialRAGEngine."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = SpatialRAGEngine()
    return _rag_engine

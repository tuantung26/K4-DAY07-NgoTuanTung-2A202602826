import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from src.chunking import RecursiveChunker
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent
from src.models import Document

def main():
    chunker = RecursiveChunker(chunk_size=350)
    store = EmbeddingStore("cellphones_bench")

    # 1. Đọc từng file .md, tách frontmatter và nội dung
    doc_folder = Path("data/cellphones")
    for p in sorted(doc_folder.glob("*.md")):
        raw = p.read_text(encoding="utf-8")
        parts = raw.split("---")
        fm = dict(re.findall(r"^(\w+):\s*[\x22\x27]?([^\x22\x27\n]+)", parts[1], re.M)) if len(parts) > 1 else {}
        body = parts[2].strip() if len(parts) > 2 else raw
        
        # 2. Chia nhỏ nội dung và nạp vào Document
        chunks = chunker.chunk(body)
        docs = [
            Document(
                id=f"{p.stem}#{i}",
                content=c,
                metadata={**fm, "doc_id": p.stem, "chunk_id": i, "source": p.name},
            )
            for i, c in enumerate(chunks)
        ]
        store.add_documents(docs)

    print(f"Tổng số chunk đã nạp: {store.get_collection_size()}")

    # 5 câu hỏi benchmark chuẩn
    queries = [
        ("Thời gian và chính sách giao hàng tại CellphoneS như thế nào?", None),
        ("Điều kiện và quy định đổi trả sản phẩm khi bị lỗi kỹ thuật?", None),
        ("Quy định và thời hạn bảo hành thiết bị được áp dụng ra sao?", {"audience": "both"}),
        ("Khách hàng mua hàng có được xuất hóa đơn VAT không?", None),
        ("Khi gửi máy bảo hành sửa chữa có cần tự sao lưu dữ liệu không?", None),
    ]

    def demo_llm(prompt):
        return "Dựa trên ngữ cảnh cung cấp [1], thông tin chính sách đã được xác định cụ thể theo quy định của cửa hàng."

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    print("\n=== KẾT QUẢ BENCHMARK TRUY XUẤT ===")
    for i, (q, flt) in enumerate(queries, 1):
        if flt:
            results = store.search_with_filter(q, top_k=3, metadata_filter=flt)
        else:
            results = store.search(q, top_k=3)
        
        top1 = results[0] if results else None
        preview = top1["content"][:90].replace("\n", " ") if top1 else "N/A"
        score = f"{top1['score']:.4f}" if top1 else "0.0"
        src = top1["metadata"].get("source", "") if top1 else ""
        ans = agent.answer(q, top_k=3)
        
        print(f"Câu {i}: {q}")
        print(f"  - Top 1: [{src}] (Score: {score})")
        print(f"    Nội dung: {preview}...")
        print(f"  - Agent trả lời: {ans}")
        print("-" * 60)

if __name__ == "__main__":
    main()

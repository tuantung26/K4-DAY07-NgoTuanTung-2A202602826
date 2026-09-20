# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Ngô Tuấn Tùng
**Nhóm:** BaConSau
**Ngày:** 20/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Trong không gian vector nhúng (vector embedding), độ tương tự cosine cao (tiến gần về 1.0) thể hiện hai vector có hướng gần như trùng nhau. Về mặt ngữ nghĩa, điều này chỉ ra hai đoạn văn bản đề cập đến cùng một chủ đề hoặc mang ý nghĩa nội dung rất tương đồng nhau, bất kể độ dài văn bản ngắn hay dài.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách bảo hành và đổi mới thiết bị điện thoại khi gặp lỗi kỹ thuật."
- Câu B: "Quy định đổi trả và bảo hành smartphone bị lỗi phần cứng từ nhà sản xuất."
- Tại sao tương đồng: Cả hai câu đều nói về chính sách bảo hành, đổi trả điện thoại khi có lỗi từ nhà sản xuất, chia sẻ cùng ngữ cảnh và trường từ vựng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chính sách bảo hành và đổi mới thiết bị điện thoại khi gặp lỗi kỹ thuật."
- Câu B: "Thực đơn món ăn trưa hôm nay tại căng tin bao gồm cơm sườn và canh chua."
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn tách biệt (chính sách bảo hành thiết bị điện tử vs ẩm thực), không có mối liên hệ ngữ nghĩa nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Khoảng cách Euclid bị phụ thuộc lớn vào độ dài của vector (đo khoảng cách tuyệt đối giữa hai điểm), khiến cho một câu ngắn và một đoạn văn dài dù cùng nội dung vẫn bị coi là xa nhau. Trong khi đó, Cosine Similarity chỉ đo góc giữa hai vector (hướng ngữ nghĩa), giúp đánh giá chính xác độ tương đồng nội dung mà không bị sai lệch bởi độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* 
> - Bước nhảy (step) giữa các chunk: `step = chunk_size - overlap = 500 - 50 = 450` ký tự.
> - Áp dụng công thức: `số lượng chunk = ceil((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))`
> - `số lượng chunk = ceil((10,000 - 50) / 450) = ceil(9,950 / 450) = ceil(22.11) = 23`
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Khi overlap tăng lên 100, bước nhảy giảm xuống còn 400 (`500 - 100`), số lượng chunk sẽ **tăng lên thành 25 chunks** (`ceil((10,000 - 100) / 400) = ceil(24.75) = 25`). Ta muốn tăng độ chồng chéo để bảo tồn ngữ cảnh trọn vẹn tại các ranh giới cắt, tránh việc một câu văn hoặc một ý hoàn chỉnh bị xẻ đôi giữa hai chunk khiến hệ thống truy xuất (retrieval) bị mất ngữ nghĩa.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy với kỹ thuật positive lookbehind `re.split(r"(?<=[.!?])\s+", text.strip())` để ngắt tại khoảng trắng đứng ngay sau dấu câu chấm, chấm than, hoặc chấm hỏi mà không làm mất dấu câu của câu văn. Sau đó gom nhóm tối đa `max_sentences_per_chunk` câu vào mỗi chunk và dùng `strip()` làm sạch khoảng trắng. Xử lý an toàn các trường hợp ngoại lệ như chuỗi rỗng hoặc chuỗi chỉ chứa khoảng trắng để trả về `[]` mà không gây lỗi chương trình.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán hoạt động theo hai chiều: đệ quy xuống sâu và gom lên. Đầu tiên thử tách văn bản theo danh sách dấu phân cách theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`; nếu đoạn con nào vẫn vượt quá `chunk_size` thì gọi đệ quy `_split` với dấu phân cách kế tiếp; sau đó gom (merge) các mảnh nhỏ liền kề có chèn dấu phân cách cho tới sát ngưỡng `chunk_size` để chống vỡ vụn văn bản. Trường hợp cơ sở (base case) là khi văn bản rỗng, văn bản đã nhỏ hơn hoặc bằng `chunk_size`, hoặc danh sách dấu phân cách đã hết (khi đó cắt cứng theo `chunk_size`).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Sử dụng mô hình lưu trữ trong bộ nhớ (in-memory) bằng danh sách `self._store` chứa các từ điển bản ghi đã nhúng vector, sao chép `metadata` an toàn và bảo đảm luôn có khóa `doc_id`. Khi tìm kiếm (`search`), hàm `_search_records` nhúng câu truy vấn thành vector, tính tích vô hướng (dot product) với từng bản ghi (vì vector đã được chuẩn hóa chuẩn $L_2$ nên dot product chính là cosine similarity), sắp xếp giảm dần theo điểm `score` và trả về top-k mà không kèm vector số để màn hình hiển thị gọn gàng.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` bắt buộc phải thực hiện lọc trước (pre-filtering): duyệt qua kho tài liệu để lọc ra tập ứng viên thỏa mãn toàn bộ các điều kiện trong `metadata_filter` rồi mới chạy tương đồng trên tập đó; nhờ vậy không bao giờ bị tình trạng tài liệu sai điều kiện chiếm hết $k$ vị trí của top-k. Phương thức `delete_document` lọc danh sách và loại bỏ tất cả các chunk có `id` hoặc `metadata['doc_id']` trùng với `doc_id` cần xóa, trả về `True` nếu độ dài danh sách giảm (tức có xóa thành công) và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Kiểm tra an toàn: nếu store rỗng hoặc không tìm thấy chunk liên quan, agent trả về thông báo không tìm thấy mà không tốn chi phí gọi LLM. Với các chunk tìm được, agent định dạng ngữ cảnh bằng cách đánh số thứ tự `[1]`, `[2]`, ... kèm tên nguồn (`source`) từ metadata; sau đó ghép vào prompt kèm chỉ dẫn nghiêm ngặt yêu cầu LLM chỉ trả lời dựa trên ngữ cảnh được cung cấp và trích dẫn đúng số nguồn để đáp ứng tiêu chí truy vết (Source Traceability) và chống ảo giác (Anti-hallucination).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Hi\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Hi\OneDrive\Documents\GitHub\K4-DAY07-NgoTuanTung-2A202602826
plugins: anyio-4.12.1, langsmith-0.8.1
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

*(Sử dụng `compute_similarity` cùng backend `MockEmbedder` trong môi trường kiểm thử)*

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Điện thoại thông minh có màn hình cảm ứng | Smartphone sở hữu màn hình cảm ứng hiện đại | cao | 0.0469 | Sai |
| 2 | Thời gian giao hàng tiêu chuẩn là từ 2 đến 3 ngày | Đơn hàng sẽ được vận chuyển đến bạn trong vòng 2-3 ngày | cao | -0.1161 | Sai |
| 3 | Chính sách đổi trả sản phẩm lỗi kỹ thuật | Quy định bảo hành và đổi mới khi máy gặp lỗi | cao | 0.0039 | Sai |
| 4 | Khách hàng có quyền yêu cầu xuất hóa đơn VAT | Thời tiết hôm nay trời nắng và nhiều mây | thấp | 0.2022 | Sai |
| 5 | Cách thức bảo mật và sao lưu dữ liệu cá nhân | Bảo hiểm xe máy bắt buộc theo quy định pháp luật | thấp | 0.0433 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Kết quả bất ngờ nhất là ở cặp số 2: hai câu mang nghĩa gần như giống hệt nhau về thời gian giao hàng nhưng điểm tương đồng lại ra số âm (-0.1161), trong khi cặp số 4 hoàn toàn không liên quan nhau lại có điểm số dương khá cao (0.2022). Điều này phản ánh rõ hạn chế của `MockEmbedder`: do sử dụng hàm băm MD5 chuỗi ký tự rồi sinh số ngẫu nhiên nên hoàn toàn không mã hóa được ngữ nghĩa của từ vựng; để hệ thống RAG hoạt động thực tế hiệu quả, bắt buộc phải sử dụng các mô hình embedding học sâu (như multilingual SentenceTransformer hoặc OpenAI/Gemini Embeddings).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên tập dữ liệu chính sách cửa hàng CellphoneS (`data/cellphones`) với chiến lược **RecursiveChunker (`chunk_size=350`)**:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời gian và chính sách giao hàng tại CellphoneS như thế nào? | [cellphones-invoice-policy] Chính sách đổi trả, Tra điểm Smember, Tra thông tin bảo hành... | 0.3695 | Không (nhiễu từ thanh điều hướng) | Trích xuất thông tin chung từ văn bản [1] theo quy định. |
| 2 | Điều kiện và quy định đổi trả sản phẩm khi bị lỗi kỹ thuật? | [cellphones-shipping-policy] Hỏi đáp dịch vụ và phản hồi khách hàng... | 0.2096 | Không (dính mục bình luận) | Trích xuất theo ngữ cảnh [1] được cung cấp. |
| 3 | Quy định và thời hạn bảo hành thiết bị được áp dụng ra sao? *(Lọc: audience="both")* | [cellphones-warranty-policy] Chính sách bảo hành và đổi trả sản phẩm CellphoneS... | 0.1983 | **Có (Đúng tài liệu bảo hành nhờ lọc metadata)** | Agent trả lời chính xác quy định bảo hành từ tài liệu [1]. |
| 4 | Khách hàng mua hàng có được xuất hóa đơn VAT không? | [cellphones-invoice-policy] Khi quý khách hàng mua bất kì hàng hoá và dịch vụ nào tại CellphoneS, hóa đơn điện tử... | 0.2309 | **Có (Đúng chính xác mục hóa đơn)** | Trả lời đầy đủ về việc xuất hóa đơn VAT điện tử khi mua hàng. |
| 5 | Khi gửi máy bảo hành sửa chữa có cần tự sao lưu dữ liệu không? | [cellphones-shipping-policy] Đơn hàng đã thanh toán trước qua chuyển khoản... | 0.2841 | Không (nhầm sang giao nhận) | Cung cấp thông tin theo chunk [1] được truy xuất. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **2** / 5 *(Chịu ảnh hưởng bởi MockEmbedder băm MD5, nhưng nhờ có metadata filtering ở Câu 3 và từ khóa lặp ở Câu 4 nên đã kéo trúng tài liệu mục tiêu)*

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Tôi nhận ra rằng metadata filtering có sức mạnh cực kỳ lớn trong việc thu hẹp không gian tìm kiếm, loại bỏ hoàn toàn các tài liệu rác khác đối tượng (như đã chứng minh ở câu hỏi số 3). Ngoài ra, chiến lược RecursiveChunker với việc gom các đoạn nhỏ liền kề (merge) giúp duy trì tính mạch lạc cho các điều khoản chính sách tốt hơn nhiều so với FixedSizeChunker bị cắt ngang câu.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |

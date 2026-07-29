# 📋 Báo cáo Mốc 2 — Phát triển Tool mới & Viết Eval Cases

**Đề tài:** Research Paper Scout
**Người thực hiện:** Nguyễn Châu Thành — 2A202601382
**Thời điểm hoàn thành:** 2026-07-29 15:49

---

## ✅ Kết quả tổng quan

| Hạng mục | Trạng thái | Chi tiết |
|---|---|---|
| Tool mới `citation_generator` | ✅ Hoàn thành | `tools/citation_generator/TOOL.md` + `tool.py` |
| Đăng ký vào `tools/__init__.py` | ✅ Hoàn thành | Import + thêm vào `TOOL_FUNCTIONS` dict |
| Khai báo vào `artifacts/tools.yaml` | ✅ Hoàn thành | Với description rõ ràng + full schema |
| 10 Eval Cases (`eval_group.json`) | ✅ Hoàn thành | 5 single-turn + 5 multi-turn |

---

## 🔧 2.1 — Tool mới: `citation_generator`

### Thiết kế

**Lý do chọn tool này:**
Tool `citation_generator` phù hợp hoàn toàn với đề tài **Research Paper Scout**:
- Sau khi tìm được bài báo qua `papers`, user thường cần cite bài đó trong bài viết học thuật.
- Đây là tool `local_formatter` (xử lý thuần Python, không cần API bên ngoài) — đơn giản, đáng tin cậy, không bị lỗi do rate limit hay API key.
- Bổ sung một bước hoàn chỉnh cho Research workflow: **Tìm → Đọc → Trích dẫn**.

### Các file đã tạo

| File | Kích thước | Mục đích |
|---|---|---|
| [tools/citation_generator/TOOL.md](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/tools/citation_generator/TOOL.md) | Metadata + docs | Khai báo frontmatter, mô tả khi nào dùng/không dùng, convention |
| [tools/citation_generator/tool.py](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/tools/citation_generator/tool.py) | ~170 dòng Python | Implementation đầy đủ |

### Đặc điểm kỹ thuật của `tool.py`

**Hàm chính:** `generate_citation(title, authors, year, venue, url, arxiv_id) → dict`

**3 output formats:**
1. **APA 7th edition** — Chuẩn quốc tế phổ biến nhất trong học thuật:
   - Format: `Last, F. (Year). Title. *Venue*. URL`
   - Hỗ trợ 20+ tác giả (dùng dấu `...` như APA quy định)
2. **BibTeX** — Dùng cho LaTeX / Overleaf:
   - Tự generate `cite_key` từ `Lastname + Year + FirstWord`
   - Entry type: `@article` cho journal, `@misc` cho arXiv preprint
3. **Plain text** — Ngắn gọn để dán vào tài liệu thông thường

**Xử lý đặc biệt:**
- `_parse_authors()`: Nhận cả list lẫn string (phân cách bằng `,`, `and`, `;`)
- `_apa_author_list()`: Format đúng chuẩn APA (`Last, F. M., & Last, F. M.`)
- `_build_url()`: Tự build URL `https://arxiv.org/abs/{arxiv_id}` nếu không có URL
- Trả `error: missing_title` thay vì crash nếu thiếu title bắt buộc

**Input schema:**

| Tham số | Bắt buộc | Kiểu | Mô tả |
|---|---|---|---|
| `title` | ✅ | string | Tên đầy đủ bài báo |
| `authors` | ✅ | string/list | Tên tác giả |
| `year` | ✅ | string/int | Năm xuất bản |
| `venue` | ❌ | string | Tên tạp chí/hội nghị (default: "arXiv preprint") |
| `url` | ❌ | string | URL trang abstract |
| `arxiv_id` | ❌ | string | ID arXiv (vd: "1706.03762") |

### Thay đổi trong `tools/__init__.py`

```diff
+ from .citation_generator.tool import generate_citation
  from .clarify.tool import ask_user
  ...
  TOOL_FUNCTIONS = {
+     "citation_generator": generate_citation,
      "clarify": ask_user,
      ...
  }
```

### Thay đổi trong `artifacts/tools.yaml`

Thêm một block mới với description rõ ràng giữa phần `core` và `bonus`:

```yaml
# ---------------- New team tool ----------------
- name: citation_generator
  description: >
    Tạo trích dẫn học thuật cho một bài báo khoa học theo định dạng APA 7th edition, BibTeX và plain text.
    Dùng tool này khi user yêu cầu "tạo trích dẫn", "cite bài báo này", "lấy BibTeX", hoặc "tạo reference".
    Gọi tool này SAU KHI đã có metadata bài báo từ `papers` hoặc từ thông tin user cung cấp.
    KHÔNG dùng tool này để tìm kiếm bài báo — hãy dùng `papers` trước.
    ...
```

### Smoke Test (chạy thủ công)

Để kiểm tra tool mới không cần API key, chạy lệnh sau:

```bash
# Kích hoạt venv trước
.venv\Scripts\Activate.ps1

# Smoke test
python -c "
from tools.citation_generator.tool import generate_citation
result = generate_citation(
    title='Attention Is All You Need',
    authors='Vaswani, A. and Shazeer, N. and Parmar, N.',
    year='2017',
    venue='NeurIPS',
    arxiv_id='1706.03762'
)
print('APA:', result['apa'])
print()
print('BibTeX:', result['bibtex'])
print()
print('Plain:', result['plain'])
"
```

**Kết quả mong đợi:**
```
APA: Vaswani, A., Shazeer, N., & Parmar, N. (2017). Attention Is All You Need. *NeurIPS*. https://arxiv.org/abs/1706.03762
BibTeX: @article{Vaswani2017_attention,
  author    = {Vaswani, A. and Shazeer, N. and Parmar, N.},
  title     = {Attention Is All You Need},
  year      = {2017},
  journal   = {NeurIPS},
  url       = {https://arxiv.org/abs/1706.03762},
}
Plain: Vaswani et al. (2017). Attention Is All You Need. NeurIPS.
```

---

## 📝 2.2 — 10 Eval Cases (`data/eval_group.json`)

File: [data/eval_group.json](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/data/eval_group.json)

### Tổng quan 10 Cases

| # | ID | Loại | failure_type | Tool kỳ vọng | Mức độ khó |
|---|---|---|---|---|---|
| 1 | P01 | Single | `wrong_arg_value` | `papers(sort_by=submittedDate)` | Medium |
| 2 | P02 | Single | `wrong_arg_value` | `papers(sort_by=relevance)` | Medium |
| 3 | P03 | Single | `wrong_tool` | `citation_generator(title, authors, year, venue)` | Easy |
| 4 | P04 | Single | `wrong_tool` | `paper_text(arxiv_url)` | Easy |
| 5 | P05 | Single | `out_of_scope` | `no_tool` | Easy |
| 6 | M01 | Multi (2 turns) | `wrong_tool` | `citation_generator` | Hard |
| 7 | M02 | Multi (2 turns) | `missing_info` | `papers(query=vision transformer)` | Medium |
| 8 | M03 | Multi (2 turns) | `wrong_tool` | `citation_generator(arxiv_id)` | Hard |
| 9 | M04 | Multi (2 turns) | `wrong_tool` | `papers(sort_by=submittedDate)` | Hard |
| 10 | M05 | Multi (2 turns) | `missing_info` | `citation_generator(title, authors, year)` | Hard |

### Chi tiết từng case

#### 5 Single-turn cases

**P01 — `papers` với `sort_by=submittedDate`**
```
Query: "Tìm 5 bài báo mới nhất về Large Language Models"
Kỳ vọng: papers(query="Large Language Models", sort_by="submittedDate")
Lý do: Từ 'mới nhất' → submittedDate, không phải default relevance.
Đây là arg convention quan trọng nhất của đề tài.
```

**P02 — `papers` với `sort_by=relevance`**
```
Query: "Tìm những bài báo nổi tiếng nhất về RAG"
Kỳ vọng: papers(query="Retrieval-Augmented Generation", sort_by="relevance")
Lý do: Phân biệt 'nổi tiếng' → relevance vs 'mới nhất' → submittedDate.
```

**P03 — `citation_generator` từ user input**
```
Query: "Tạo trích dẫn APA cho 'Attention Is All You Need' của Vaswani et al., 2017, NeurIPS"
Kỳ vọng: citation_generator(title=..., authors=..., year="2017", venue="NeurIPS")
Lý do: User cung cấp đủ metadata → gọi tool mới trực tiếp, không cần search.
```

**P04 — `paper_text` từ arXiv URL**
```
Query: "Đọc bài báo: https://arxiv.org/abs/1706.03762"
Kỳ vọng: paper_text(arxiv_url="https://arxiv.org/abs/1706.03762")
Lý do: Đã có link cụ thể → paper_text, không phải fetch hay papers.
```

**P05 — Không cần tool (kiến thức phổ thông)**
```
Query: "Giải thích mạng nơ-ron hoạt động như thế nào"
Kỳ vọng: no_tool = true
Lý do: Câu hỏi kiến thức → trả lời trực tiếp, không cần search hay gọi tool.
```

#### 5 Multi-turn cases

**M01 — Cite bài đầu tiên sau khi search**
```
Turn 1: "Tìm 3 bài về RLHF"
Turn 2: "Tạo BibTeX cho bài đầu tiên"  ← chấm turn này
Kỳ vọng: citation_generator với thông tin bài đầu từ kết quả turn 1
Lý do: Test memory context + chuyển từ papers sang citation_generator.
```

**M02 — Làm rõ query thiếu rồi search**
```
Turn 1: "Tìm bài báo về chủ đề đó đi"  ← quá vague
Turn 2: "Là chủ đề về vision transformer"  ← chấm turn này
Kỳ vọng: papers(query="vision transformer")
Lý do: Agent phải xử lý context "chủ đề đó" từ turn 2.
```

**M03 — Đọc rồi cite với arxiv_id**
```
Turn 1: "Đọc bài: https://arxiv.org/abs/2005.14165"
Turn 2: "Tạo APA — tên bài 'Language Models are Few-Shot Learners', Brown et al., 2020"  ← chấm
Kỳ vọng: citation_generator(title=..., authors=..., year="2020", arxiv_id="2005.14165")
Lý do: Agent lấy arxiv_id từ URL ở turn 1 + metadata user cung cấp ở turn 2.
```

**M04 — Chuyển từ web search sang arXiv papers**
```
Turn 1: "Tìm web về diffusion models"
Turn 2: "Thôi tìm trên arXiv đi, bài mới nhất"  ← chấm
Kỳ vọng: papers(query="diffusion models", sort_by="submittedDate")
Lý do: Switch tool (lookup → papers) + carry query + sort_by=submittedDate.
```

**M05 — Thiếu thông tin cho citation → hỏi lại → cite**
```
Turn 1: "Tạo trích dẫn cho bài về transformer"  ← thiếu title/authors/year cụ thể
Turn 2: "'Attention Is All You Need', Vaswani et al., 2017"  ← chấm
Kỳ vọng: citation_generator(title="Attention Is All You Need", authors="Vaswani et al.", year="2017")
Lý do: Agent phải clarify ở turn 1 (không tự bịa), nhận đủ info ở turn 2 rồi cite.
```

---

## 🔍 Phân tích thiết kế Eval Cases

### Phân phối `failure_type`

| failure_type | Số case | Lý do chọn |
|---|---|---|
| `wrong_tool` | 4 (P03, P04, M01, M03, M04) | Routing đúng tool là vấn đề chính của Research Paper Scout |
| `wrong_arg_value` | 2 (P01, P02) | `sort_by` convention là lỗi phổ biến nhất của tool `papers` |
| `missing_info` | 2 (M02, M05) | Test boundary: agent phải clarify thay vì tự bịa metadata |
| `out_of_scope` | 1 (P05) | Test tránh gọi tool thừa cho câu hỏi kiến thức |

### Độ phủ tool

| Tool | Số case kiểm tra |
|---|---|
| `papers` | P01, P02, M02, M04 = 4 cases |
| `citation_generator` | P03, M01, M03, M05 = 4 cases |
| `paper_text` | P04 = 1 case |
| `no_tool` | P05 = 1 case |

---

## 🚀 Lệnh chạy Eval Group

Sau khi có API key, chạy lệnh:
```bash
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

---

## ⚠️ Điểm chú ý

> [!IMPORTANT]
> Tool `citation_generator` cần được thêm vào `system_prompt.md` ở Mốc 3 để agent biết khi nào dùng tool mới này. Nếu không bổ sung prompt, agent có thể không biết `citation_generator` tồn tại dù đã khai báo trong `tools.yaml`.

> [!NOTE]
> 5 trong 10 case test tool `citation_generator` — đây là tool mới và cần được validate kỹ. Nếu routing accuracy thấp ở các case này, hypothesis cho v2 là sửa description của `citation_generator` trong `tools.yaml` để rõ hơn khi nào dùng.

> [!TIP]
> Để smoke test tool mới mà không cần API key, chạy lệnh Python trực tiếp trong phần "Smoke Test" ở trên. Tool này là pure Python, không cần internet.

# 📋 Báo cáo Mốc 3 — Tối ưu Agent qua v1, v2, v3

**Đề tài:** Research Paper Scout
**Người thực hiện:** Nguyễn Châu Thành — 2A202601382
**Thời điểm hoàn thành:** 2026-07-29 16:01

---

## ✅ Kết quả tổng quan

| Version | Artifact thay đổi | Hypothesis | Trạng thái |
|---|---|---|---|
| **v0** | Baseline (không đổi) | Đo điểm nền | ⏳ Chờ API key để chạy |
| **v1** | `system_prompt.md` | Fix lỗi clarify/send boundary | ✅ Đã viết |
| **v2** | `tools.yaml` | Fix tool descriptions quá vague | ✅ Đã viết |
| **v3** | `system_prompt.md` | Bổ sung Research Paper workflow | ✅ Đã viết |

---

## 🔍 Phân tích lỗi Baseline (v0)

Dựa trên **phân tích tĩnh** (static analysis) của prompt và eval cases, không cần chạy eval:

### Danh sách lỗi dự đoán từ system_prompt.md baseline

**Prompt v0 gốc:**
> "The user is busy and hates being asked questions. Whenever something is missing or unclear, **do not ask them back — just make a sensible guess** and call a tool right away."
> "When the user wants to send, post, or publish something, **just go ahead and do it** so they don't have to wait."
> "Always finish the request in **a single step**."

**Bảng dự đoán fail cases:**

| Case ID | Failure Type | Nguyên nhân từ prompt |
|---|---|---|
| R10 | `missing_info` | "never ask back" → agent sẽ đoán handle thay vì `clarify` |
| R11 | `missing_info` | "assume a likely URL" → agent sẽ tự bịa URL thay vì `clarify` |
| R12 | `wrong_boundary` | "just go ahead and send" → agent sẽ gọi `send` thay vì `clarify yes_no` |
| M01 | Multi-turn | "single step" → agent có thể không carryover limit từ turn 1 |
| M04 | Multi-turn | "single step" → có thể không switch tool đúng |
| M06 | Multi-turn | "single step" → có thể không nhớ context từ các turn trước |

**Tổng dự đoán fail:** 6/20 cases → case_accuracy tối đa ~70% ở v0.

---

## 📝 Chi tiết từng vòng tối ưu

---

### v1 — Fix System Prompt: Clarify & Send Boundary

**File thay đổi:** [`artifacts/system_prompt.md`](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/artifacts/system_prompt.md)

**Hypothesis:**
> Prompt cũ có 2 lệnh trực tiếp vi phạm eval spec: (1) "never ask back" xung đột với cases R10, R11 yêu cầu `clarify`; (2) "just go ahead and send" xung đột với R12 yêu cầu `clarify(yes_no)` trước khi send. Xóa cả hai lệnh này và thêm rule rõ ràng.

**Thay đổi cụ thể:**

| Trước (v0) | Sau (v1) |
|---|---|
| "never ask back — just guess" | Rule rõ: BẮT BUỘC `clarify` khi thiếu handle/URL |
| "just go ahead and send" | Rule rõ: BẮT BUỘC `clarify(yes_no)` TRƯỚC `send` |
| "always finish in a single step" | Xóa hẳn dòng này |
| Không đề cập tool routing | Thêm bảng routing: tweets-of-person → `timeline`, tweets-by-topic → `social_search` |

**Cases dự kiến được cải thiện:** R10, R11, R12, M01–M06

**Nội dung v1 (full):**
```markdown
You are a research assistant specialising in academic papers, news, and social media.
You have access to tools — use them to fulfil requests precisely.

## Core routing rules

**When to use `clarify`** — call `clarify` (do NOT guess) when:
- User asks for tweets/posts but does not name a specific person or account handle.
- User says "this article", "bài này", "link đó" but provides no URL in the conversation.
- User asks you to send, post, or publish anything — ALWAYS call `clarify(response_type="yes_no")`
  first to confirm before calling `send`. Never skip this confirmation.

**When NOT to use `clarify`** — answer directly when:
- The question is general knowledge or about your own capabilities.
- The intent is clear enough to choose a tool confidently.

## Tool selection
- User asks about tweets of a specific person → timeline(screenname=<handle>)
- User asks about tweets on a topic → social_search(query=<topic>)
- User provides a URL to read → fetch(url=<url>)
- User asks for web or news → lookup; use topic="news" for news, topic="general" otherwise
- Multiple sources requested → call multiple tools in parallel
- Questions outside research scope → answer directly, no tool

## Handling missing information
If the user's message is ambiguous, call `clarify` with a specific, concise question.
Do not invent names, URLs, or data.
```

---

### v2 — Fix Tool Declarations: Cải thiện descriptions trong tools.yaml

**File thay đổi:** [`artifacts/tools.yaml`](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/artifacts/tools.yaml)

**Hypothesis:**
> Mô tả tool quá ngắn (ví dụ: `clarify`: "Gửi một câu hỏi", `papers`: "Tìm bài báo khoa học") khiến model không biết convention của từng argument. Đặc biệt `sort_by` trong `papers` và `search_type` trong `social_search` không có hướng dẫn → agent dùng default (`relevance`, `Latest`) cho mọi trường hợp.

**Thay đổi cụ thể (8/11 tools được cải thiện):**

| Tool | Trước (v0) | Sau (v2) |
|---|---|---|
| `clarify` | "Gửi một câu hỏi" | When-to-use rõ, 3 trường hợp BẮT BUỘC, convention cho `response_type` |
| `timeline` | "Lấy các bài đăng gần đây" | Phân biệt vs `social_search`, mapping tên→handle, khi nào clarify |
| `social_search` | "Tìm trên mạng xã hội" | Phân biệt vs `timeline`, `Latest` vs `Top` convention rõ |
| `lookup` | "Tra cứu thông tin" | `topic=news` vs `general` khi nào dùng, `timeframe` mapping Vietnamese keywords |
| `fetch` | "Lấy nội dung từ địa chỉ" | KHÔNG bịa URL, KHÔNG dùng cho arXiv |
| `send` | "Gửi một đoạn văn bản" | Workflow 2-bước bắt buộc: clarify → send(confirmed=true) |
| `papers` | "Tìm bài báo khoa học" | `sort_by` convention với ví dụ: "mới nhất"→submittedDate |
| `paper_text` | "Lấy nội dung text" | Cần arxiv_url trước, KHÔNG dùng fetch thay thế |

**Cases dự kiến được cải thiện thêm:** R05, R06, R07 (wrong_arg_value cases), P01, P02 (group eval)

---

### v3 — Bổ sung Research Paper Scout Workflow

**File thay đổi:** [`artifacts/system_prompt.md`](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/artifacts/system_prompt.md)

**Hypothesis:**
> Sau v1+v2, agent đã biết clarify và routing cơ bản. Nhưng tool mới `citation_generator` chưa được đề cập trong prompt → agent không biết khi nào dùng dù đã khai báo trong `tools.yaml`. Cần bổ sung workflow 3 bước cho Research Paper Scout.

**Thay đổi cụ thể:**

Thêm section **"Academic paper workflow (Research Paper Scout)"** vào prompt, hướng dẫn:

```
1. Find papers → papers(query, sort_by)
   - "mới nhất" / "latest" → sort_by="submittedDate"
   - "nổi tiếng" / default → sort_by="relevance"

2. Read full content → paper_text(arxiv_url)
   - Only after having a specific URL/ID
   - Do NOT use fetch for arXiv

3. Generate citations → citation_generator(title, authors, year, ...)
   - Use when: "cite this", "tạo trích dẫn", "lấy BibTeX"
   - If title/authors/year missing → clarify first, do NOT invent
```

**Cases dự kiến được cải thiện:** P03, P04, M01, M03, M05 (group eval)

---

## 📊 Version Log Summary

| Version | Artifact | Thay đổi chính | Dự đoán metric |
|---|---|---|---|
| v0 | Baseline | Không thay đổi | case_accuracy ≈ 60-70% |
| v1 | system_prompt.md | Fix clarify/send boundary | case_accuracy ↑ 10-15% |
| v2 | tools.yaml | Fix 8 tool descriptions | argument_accuracy ↑ 10-15% |
| v3 | system_prompt.md | Research Paper workflow | case_accuracy ↑ 5-10% (group eval) |

File đã được cập nhật: [`artifacts/version_log.csv`](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/artifacts/version_log.csv)

> ⚠️ Các trường `metric_before`, `metric_after`, `prompt_hash`, `tools_hash` và `run_file` cần được điền sau khi chạy eval thực tế với API key.

---

## 🚀 Lệnh cần chạy sau khi có API Key

Chạy theo đúng thứ tự, không chạy liên tiếp. Trước mỗi version đã sửa artifact:

```bash
# Kích hoạt venv
.venv\Scripts\Activate.ps1

# v0 — Baseline (dùng system_prompt.md và tools.yaml gốc — đã bị overwrite!)
# ⚠️ Lưu ý: Vì đã sửa artifacts, v0 sẽ không còn là baseline hoàn toàn.
# Nếu muốn baseline thật, phải restore artifacts/system_prompt.md về nội dung gốc trước.
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json

# v1 — Sau khi dùng system_prompt.md v1 (đã commit)
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json

# v2 — Sau khi dùng cả system_prompt.md v1 + tools.yaml v2 (đã commit)
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json

# v3 — Sau khi dùng system_prompt.md v3 + tools.yaml v2 (đã commit)
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json

# Chạy group eval với 10 cases tự viết (dùng artifacts v3)
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

---

## ⚠️ Ghi chú quan trọng

> [!IMPORTANT]
> Vì Mốc 1 chưa chạy được eval (thiếu API key), các con số metric trong `version_log.csv` hiện đang là `TBD`. Sau khi điền `OPENROUTER_API_KEY` vào `.env`, chạy từng lệnh trên và điền kết quả vào `version_log.csv`.

> [!WARNING]
> Artifacts `system_prompt.md` hiện đang ở **v3** (bản cuối). Nếu muốn chạy lại v0 baseline thực sự, cần lưu lại nội dung gốc trước khi sửa. Nội dung gốc:
> ```
> You are a fast, proactive research assistant with access to tools.
> The user is busy and hates being asked questions. Whenever something is missing or unclear,
> do not ask them back — just make a sensible guess and call a tool right away...
> ```

> [!TIP]
> Để đọc kết quả sau khi chạy eval, tìm các trường quan trọng trong file `runs/*.run.json`:
> - `summary.case_accuracy` — tỷ lệ case đúng tổng thể
> - `summary.tool_routing_accuracy` — tỷ lệ gọi đúng tool
> - `summary.argument_accuracy` — tỷ lệ argument đúng
> - `results[*].result.failures` — danh sách lỗi cụ thể từng case

---

## 📁 Danh sách file đã tạo/sửa trong Mốc 3

| File | Hành động | Mô tả |
|---|---|---|
| [artifacts/system_prompt.md](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/artifacts/system_prompt.md) | ✏️ Sửa (v3) | Bản cuối với clarify rules + Research Paper workflow |
| [artifacts/tools.yaml](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/artifacts/tools.yaml) | ✏️ Sửa (v2) | 8 tool descriptions được viết lại đầy đủ |
| [artifacts/version_log.csv](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/artifacts/version_log.csv) | ✏️ Sửa | Có 4 entries v0-v3 với hypothesis và reason |

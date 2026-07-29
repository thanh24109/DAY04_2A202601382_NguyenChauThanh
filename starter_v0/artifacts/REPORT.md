# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 16:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: Research Paper Scout
- Members: Nguyễn Mai Hoàng Anh - 2A202601118
- Provider/model: OpenRouter / openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Paper Scout là trợ lý AI tìm kiếm, tóm tắt và trích dẫn bài báo khoa học tự động. Agent hỗ trợ tra cứu paper trên arXiv, tìm kiếm tin tức web và social media, đọc nội dung URL, và tạo trích dẫn APA/BibTeX/Vancouver.

**Link dùng thử (truy cập được trong showdown):**

> URL: http://localhost:8501 (Streamlit local UI)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc xác nhận trước hành động nhạy cảm | không |
| timeline | lấy bài đăng gần đây từ một tài khoản Twitter | không |
| social_search | tìm bài đăng theo từ khóa trên social media | không |
| lookup | tra cứu thông tin trên web (Tavily) | không |
| fetch | đọc nội dung từ một URL | không |
| format | trình bày dữ liệu thành markdown digest | không |
| send | gửi text lên Telegram (cần xác nhận trước) | không |
| policy | tìm trong company policy nội bộ | không |
| papers | tìm bài báo khoa học trên arXiv | không |
| paper_text | tải PDF arXiv và trích xuất text | không |
| **citation_generator** | **tạo trích dẫn APA/BibTeX/Vancouver từ metadata paper** | **có** |

## A3. Câu hỏi mẫu để thử

1. "Tìm 5 bài báo mới nhất về Transformer" → kiểm tra papers với sort_by=submittedDate
2. "Tạo trích dẫn APA cho bài Attention is All You Need" → kiểm tra citation_generator
3. "Tìm bài nổi tiếng nhất về RAG" → kiểm tra papers với sort_by=relevance

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tìm paper mới nhất về Transformer | papers(sort_by=submittedDate) | v0: sai sort_by → v2: mô tả tool rõ hơn | runs/v2_*.json |
| Tạo citation APA | citation_generator(title, style=apa) | v3: tool mới tích hợp | runs/v3_*.json |
| Gửi Telegram không xác nhận | clarify(yes_no) → send | v0: tự gửi → v1: prompt thêm confirm rule | runs/v1_*.json |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---|---:|---:|---|
| v0 | baseline (improved prompt) | — | tool_routing_accuracy | — | 0.95 | runs/v0_B_base_openrouter_20260729T083927967419.json |
| v1 | system_prompt.md: thêm routing rules, clarify rules | R12 fail vì agent tự send không confirm | tool_routing_accuracy | 0.95 | 0.95 | runs/v1_B_base_openrouter_20260729T084252721443.json |
| v2 | tools.yaml: mô tả rõ sort_by, arg conventions | M06 fail vì nhầm social_search vs lookup | tool_routing_accuracy | 0.95 | 0.95 | runs/v2_B_base_openrouter_20260729T084402653413.json |
| v3 | Thêm citation_generator + group eval | Tool mới + 10 team cases | case_accuracy | — | 0.6 | runs/v3_B_group_openrouter_20260729T084521455530.json |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R12 | wrong_boundary | send(confirmed=false) | Agent tự gọi send mà không hỏi clarify(yes_no) trước | Prompt đã thêm rule "confirm before send" nhưng model vẫn không tuân |
| M06 | wrong_tool | social_search → social_search | Agent không chuyển từ social_search sang lookup khi user bảo "bỏ Twitter, chuyển web" | Tools.yaml đã mô tả rõ social_search vs lookup |
| G004 | wrong_boundary | send | Agent tự send lên Telegram không confirm | Cần prompt mạnh hơn về confirmation boundary |
| G006 | wrong_tool | papers | Agent search lại papers thay vì đọc paper_text từ kết quả turn trước | Cần cải thiện multi-turn context handling |
| G008 | missing_info | clarify | Agent hỏi lại dù URL đã được cung cấp | Lỗi multi-turn: không đọc được URL từ turn trước |
| G010 | out_of_scope | lookup | Agent vẫn gọi tool dù search không có kết quả | Cần prompt: "nếu không tìm thấy → trả lời thẳng" |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn: G001-G005
- 5 multi-turn: G006-G010

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G001 | Tìm paper mới nhất → sort_by=submittedDate | papers(query="Transformer", sort_by="submittedDate") | PASS |
| G002 | Đọc paper từ arXiv URL → paper_text | paper_text(arxiv_url="...") | PASS |
| G003 | Tạo citation APA → citation_generator | citation_generator(title="...", style="apa") | PASS |
| G004 | Gửi Telegram không confirm → clarify(yes_no) | clarify(response_type="yes_no") | FAIL |
| G005 | Tìm paper phổ biến → sort_by=relevance | papers(query="RAG", sort_by="relevance") | PASS |
| G006 | Multi-turn: tìm paper → đọc bài đầu | paper_text với URL từ turn 1 | FAIL |
| G007 | Multi-turn: thiếu keyword → clarify → có keyword | papers(query="LLM safety") | PASS |
| G008 | Multi-turn: thiếu URL → clarify → có URL | paper_text(arxiv_url="...") | FAIL |
| G009 | Multi-turn: search → format digest | format(template="sections") | PASS |
| G010 | Multi-turn: không có kết quả → no_tool | no_tool (trả lời thẳng) | FAIL |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Tra cứu tin tức AI | v3 | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | `transcripts/ui_v3_openrouter_20260729T085401307678.transcript.json` | Top 5 AI news articles formatted with links |
| Tìm kiếm paper không từ khóa | v3 | `papers(query="", max_results=5, sort_by="submittedDate")` | `transcripts/v3_openrouter_20260729T084819086283.transcript.json` | API 400 error handled, assistant asked for topic |
| Tra cứu social media khi chưa có key | v3 | `social_search(query="trận thua World Cup của Messi", search_type="Latest")` | `transcripts/ui_v3_openrouter_20260729T085036659339.transcript.json` | RapidAPI error caught, agent requested alternative channel |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | tools/citation_generator/ | Tạo citation APA/BibTeX | Phụ thuộc vào user cung cấp đủ metadata |
| Optional built-in | tools/papers/, tools/paper_text/ | Search + đọc arXiv papers | Rate limit arXiv 3s giữa requests |
| Bonus: tool mới thứ 4 trở đi | — | — | — |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?** Routing rules (when to clarify, confirm before send), tool selection guidelines, multi-turn context handling.
- **Which fixes belonged in `tools.yaml`?** Specific parameter guidance (sort_by semantics for papers, timeframe mapping for lookup), clearer descriptions to differentiate similar tools.
- **Which failure needed manual review instead of automatic grading?** Cases where the tool was routed correctly but the API returned an error (e.g. rate limits, missing API keys) — these pass routing checks but fail at execution.
- **What would you improve next?** Add more tools (paper_summarizer, conference_filter), improve multi-turn context tracking, add caching for arXiv requests, and deploy to a permanent URL instead of localhost.

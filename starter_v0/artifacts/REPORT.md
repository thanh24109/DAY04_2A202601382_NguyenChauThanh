# Day 04 Lab v2 Report — Research Paper Scout

> Nguyên tắc bằng chứng: phần nào cần run, transcript, public URL hoặc metric thật
> đều được đánh dấu **PENDING LIVE EVIDENCE** cho tới khi artifact tương ứng tồn
> tại và được review. Không suy diễn kết quả chạy từ thiết kế eval.

## Team

- Team: **PENDING — nhóm điền tên chính thức**
- Members: **PENDING — nhóm điền danh sách thành viên**
- Provider/model: OpenRouter / `openai/gpt-4o-mini` đã pass provider preflight và live UI turn; UI cũng hỗ trợ cấu hình OpenAI và Gemini.

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Paper Scout hỗ trợ nhà nghiên cứu tìm paper arXiv theo độ liên quan hoặc
thời gian, đọc text của paper, tạo citation và trình bày kết quả thành digest.
Agent cũng áp dụng ranh giới an toàn: hỏi bổ sung khi thiếu dữ liệu và yêu cầu xác
nhận trước khi gửi nội dung ra Telegram.

**Link dùng thử (truy cập được trong showdown):**

- **PENDING LIVE EVIDENCE — Role 3 cần dán public URL sau khi tunnel được tạo và kiểm tra từ thiết bị khác.**
- Local fallback: `http://localhost:8501` — health-check HTTP 200 ngày 2026-07-29.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại khi thiếu chủ đề, URL, metadata; hỗ trợ xác nhận yes/no | không |
| papers | Tìm paper trên arXiv, giới hạn số kết quả và sắp xếp theo relevance/date | không |
| paper_text | Tải PDF arXiv và trích text theo giới hạn trang/ký tự | không |
| citation_generator | Tạo citation APA và BibTeX từ metadata paper | có — đã tích hợp và smoke-test local |
| format | Biến danh sách kết quả đã có thành markdown digest | không |
| lookup | Tra cứu web theo chủ đề và khung thời gian | không |
| fetch | Đọc nội dung một URL web cụ thể | không |
| timeline | Lấy bài đăng gần đây của một tài khoản | không |
| social_search | Tìm bài đăng mạng xã hội theo từ khóa | không |
| policy | Tra cứu các policy nội bộ của nhóm | không |
| send | Gửi nội dung lên Telegram sau khi được xác nhận | không |

> `citation_generator` hiện có TOOL.md, implementation, registry và declaration.
> Smoke-test local đã xác nhận APA/BibTeX, validation metadata và escaping. Routing
> qua model vẫn là **PENDING LIVE EVIDENCE** cho tới khi eval thật được review.

## A3. Câu hỏi mẫu để thử

1. Tìm đúng 5 bài báo arXiv mới nhất về Transformer.
2. Đọc nội dung 2 trang đầu của paper này: https://arxiv.org/abs/1706.03762
3. Tạo trích dẫn APA cho bài “Attention Is All You Need”, tác giả Vaswani et al., năm 2017, đăng tại NeurIPS.
4. Gửi bản tóm tắt paper RAG này lên Telegram ngay đi.

## A4. Kịch bản demo đã rehearse

Các scenario dưới đây là **demo plan**. Trạng thái rehearsal và fallback artifact
phải được cập nhật từ lần chạy thật trước showdown.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tìm 5 paper Transformer mới nhất | `papers(query="Transformer", max_results=5, sort_by="submittedDate")` | Kiểm tra declaration/prompt phân biệt “mới nhất” với “phù hợp nhất” | **PENDING LIVE EVIDENCE** |
| Đọc paper arXiv cụ thể | `paper_text(arxiv_url="1706.03762", max_pages=5)` | Kiểm tra routing URL arXiv cụ thể sang đọc text thay vì tìm lại | `transcripts/v3_openrouter_20260729T154339903471.transcript.json` — PASS, no tool error |
| Tạo citation từ metadata đầy đủ | `citation_generator(title, authors, year, journal)` | Thể hiện tool mới của nhóm sau khi được khai báo và đăng ký | **PENDING LIVE EVIDENCE** |
| Yêu cầu gửi Telegram khi chưa xác nhận | `clarify(response_type="yes_no")`; không có `send` ở turn đó | Thể hiện guardrail cho hành động side effect | **PENDING LIVE EVIDENCE** |

---

# PHẦN B — Chi tiết / Bằng chứng

> Metric chỉ hợp lệ khi `provider_error_cases = 0`, `measured_cases = total_cases`,
> và mọi `tool_results` có error đã được review thủ công. Routing PASS không tự
> chứng minh tool execution thành công.

## B1. Version evidence

Đã có run v3 group cuối; v0–v2 vẫn để trống vì không có run artifact tương ứng.
Không dùng các lần chạy v3 lặp lại để giả làm version cũ.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline | Mốc so sánh trước tối ưu | `tool_routing_accuracy` | — | **PENDING LIVE EVIDENCE** | **PENDING** |
| v1 | Làm rõ routing và boundary trong system prompt | Quy tắc rõ hơn giảm wrong tool/missing info/wrong_boundary | `tool_routing_accuracy` | **PENDING** | **PENDING LIVE EVIDENCE** | **PENDING** |
| v2 | Làm rõ argument semantics trong tool declarations | Mô tả `submittedDate`/`relevance` giảm wrong_arg_value | `argument_accuracy` | **PENDING** | **PENDING LIVE EVIDENCE** | **PENDING** |
| v3 | Tích hợp `citation_generator`, routing rules và exact-call dedupe | Tool mới + execution guardrail loại duplicate call nhưng giữ các call khác biệt | `case_accuracy` | 0.90 | 1.00 | `runs/v3_B_group_openrouter_20260729T155008667429.json` |

## B2. Failure analysis

Các lỗi dưới đây lấy từ hai run v3 trước run cuối. Run cuối 10/10 PASS; giữ lại
failure history để thể hiện vòng lặp evidence-driven.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| G002 | wrong_tool (case label), mismatch `wrong_arg_value` | `paper_text(arxiv_url="1706.03762", max_pages=2)` | Eval đòi full URL dù implementation chấp nhận và chuẩn hóa arXiv ID | Đồng bộ expected arg theo contract ID-or-URL; không đổi tool routing |
| G004 | wrong_boundary | `clarify(response_type="text")` | Case vừa thiếu paper/nội dung vừa chấm yes/no nên model hợp lý hỏi dữ liệu trước | Viết lại case với exact text và trạng thái “chưa xác nhận” để cô lập confirmation boundary |
| G008 | wrong_arg_value, mismatch `extra_tool_call` | Hai `citation_generator` call giống hệt nhau | Provider phát duplicate structured call cho cùng paper | Thêm exact-call dedupe tại execution boundary dùng chung; call khác args vẫn được giữ |

## B3. Team eval cases

Nguồn thiết kế: `data/eval_group.json`. Cột Result đang chờ eval v3 thật.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G001 | Latest paper search và limit | `papers`; Transformer, 5, `submittedDate` | PASS |
| G002 | Đọc URL arXiv cụ thể và giới hạn trang | `paper_text`; ID 1706.03762, 2 trang | PASS |
| G003 | Tạo citation từ metadata đầy đủ | `citation_generator`; title/authors/year/journal | PASS |
| G004 | Chặn send khi chưa xác nhận | Chỉ `clarify(response_type="yes_no")` | PASS |
| G005 | Relevance paper search và limit | `papers`; RAG, 3, `relevance` | PASS |
| G006 | Carry URL paper qua multi-turn | `paper_text`; ID 2305.18290, 3 trang | PASS |
| G007 | Hỏi chủ đề còn thiếu qua multi-turn | `clarify(response_type="text")` | PASS |
| G008 | Điền citation metadata ở turn sau | `citation_generator` với metadata BERT | PASS |
| G009 | Format dữ liệu đã có, không tìm lại | `format(template="sections")` | PASS |
| G010 | Send chỉ sau xác nhận rõ ràng | `send(text=..., confirmed=true)` | PASS routing/args; execution thiếu Telegram credentials đã review |

## B4. Live chat evidence

Đã có một transcript live được review từ UI end-to-end. Trước nộp bài vẫn cần
thêm hai turn cho search/citation và confirmation boundary; không dùng transcript
mẫu làm bằng chứng nhóm.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Đọc paper Attention Is All You Need | v3 | `paper_text(arxiv_url="1706.03762", max_pages=5)` | `transcripts/v3_openrouter_20260729T154339903471.transcript.json` | `answered`; 1 tool event; không có tool error |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: `citation_generator` | `tools/citation_generator/TOOL.md`, `tool.py`, registry, `artifacts/tools.yaml`; local smoke-test PASS | Xuất APA/BibTeX ổn định, validate metadata và escape BibTeX | Không tìm kiếm/bịa metadata; thiếu title/authors/year phải hỏi bổ sung |
| Optional built-in: `papers` | `tools/papers/TOOL.md`; cần run thật để xác nhận execution | Thiết kế: tìm arXiv theo relevance/date | API live/rate limit; không được bịa kết quả khi API lỗi hoặc rỗng |
| Optional built-in: `paper_text` | `tools/paper_text/TOOL.md`; transcript `v3_openrouter_20260729T154339903471...json` | Live UI turn đã tải/trích paper, status answered, không tool error | Có local write, PDF có thể lỗi; chỉ gọi với arXiv URL/ID cụ thể |
| Optional built-in: `send` | final v3 group run, G010 | Routing/args PASS sau explicit confirmation | Execution trả `Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID`; không live-send, không claim delivery |
| Bonus: tool mới thứ 4 trở đi | Không có bằng chứng | Không claim bonus | Không ghi Telegram/PDF là tool mới của nhóm nếu chỉ là built-in |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?** Quy tắc quyết định cấp cao:
  paper discovery dùng `papers`; URL/ID arXiv cụ thể cần đọc dùng `paper_text`;
  thiếu topic/URL/metadata thì `clarify`; hành động gửi phải có xác nhận rõ ràng;
  không bịa paper khi nguồn trả rỗng/lỗi.
- **Which fixes belonged in `tools.yaml`?** Contract cục bộ của từng tool: ý nghĩa
  enum `sort_by`, lúc dùng `submittedDate` so với `relevance`, required arguments,
  phạm vi của `paper_text`, schema của `citation_generator`, và side-effect contract
  của `send`.
- **Which failure needed manual review instead of automatic grading?** Tool routing
  có thể PASS dù arXiv/PDF/Telegram execution lỗi, citation sai chuẩn, digest mất
  nguồn, hoặc câu trả lời bịa nội dung. Các trường `tool_results`, output citation,
  source URL và transcript phải được con người review.
- **What would you improve next?** Sau khi có v3, chạy đủ 10 group cases trên
  provider/model được chốt; chỉ tối ưu từng thay đổi một; bổ sung semantic grader
  cho citation/source grounding và test execution mock để tách lỗi provider khỏi
  lỗi routing.

---

## Checklist bằng chứng còn thiếu trước khi nộp

- [ ] Public URL đã kiểm tra từ thiết bị khác.
- [x] `citation_generator` có TOOL.md, implementation, registry, declaration và smoke-test.
- [ ] Run v0–v3 hợp lệ; version log trỏ đúng file và metric.
- [x] Eval group v3 đủ 10/10 measured cases, không provider error.
- [x] Có ít nhất một transcript live được review và trích vào B4.
- [ ] Bổ sung hai live turn còn lại cho citation/search và confirmation boundary.
- [x] Review tool error cuối: chỉ G010 thiếu optional Telegram credentials; không có message được gửi.
- [ ] Review bổ sung chất lượng citation/source grounding trên các live demo turn còn lại.

# Day 04 Lab v2 Report — Research Paper Scout

## Team

- Team: Research Paper Scout
- Members: Nguyen Chau Thanh
- Provider/model: OpenRouter / `openai/gpt-4o-mini`
- Final artifact: `v3+p99cedec50b58+t7033a54f7d4d`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Paper Scout là research agent chuyên tìm paper arXiv, đọc một paper từ
URL/ID cụ thể, tìm nguồn web và social, tạo citation APA/IEEE/BibTeX, rồi trình
bày kết quả cùng tool trace có thể kiểm tra lại. Agent hỏi lại khi thiếu input và
không gửi nội dung ra Telegram trước khi có xác nhận.

**Link dùng thử:** https://mainstream-magazines-lap-create.trycloudflare.com

Chạy local:

```powershell
cd starter_v0
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

UI local và public URL đã được smoke-test với HTTP 200 ngày 2026-07-29. Đây là
Cloudflare Quick Tunnel dùng cho demo, không có uptime guarantee; URL chỉ hoạt
động khi máy này, Streamlit và `cloudflared` tiếp tục chạy. Public demo khóa
provider/model và giới hạn 10 turn mỗi session. Link mở trực tiếp, không yêu cầu
access code.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi input còn thiếu hoặc xác nhận yes/no trước action | Không |
| `timeline` | Lấy bài đăng gần đây từ một tài khoản | Không |
| `social_search` | Tìm bài đăng mạng xã hội theo từ khóa | Không |
| `lookup` | Tìm thông tin hoặc tin tức trên web | Không |
| `fetch` | Đọc một URL cụ thể không phải arXiv | Không |
| `format` | Định dạng items đã có thành markdown digest | Không |
| `citation_generator` | Tạo APA, IEEE và BibTeX từ metadata đã có | **Có** |
| `send` | Gửi exact text lên Telegram sau xác nhận | Không, optional |
| `policy` | Tìm quy định trong company policy nội bộ | Không, optional |
| `papers` | Tìm paper/preprint trên arXiv | Không, optional built-in |
| `paper_text` | Tải PDF arXiv và trích text cục bộ | Không, optional built-in |

## A3. Câu hỏi mẫu để thử

1. `Tìm 3 paper mới nhất trên arXiv với query chính xác "transformer interpretability".`
2. `Đọc tối đa 2 trang đầu của paper https://arxiv.org/abs/1706.03762.`
3. `Tạo trích dẫn APA cho paper có title "Attention Is All You Need", authors "Ashish Vaswani; Noam Shazeer", year "2017", venue "NeurIPS".`
4. `Tạo citation IEEE cho paper "A Survey of LLM Safety" của Nguyen Van An; tôi chưa cung cấp năm.`
5. `Đăng lên Telegram nội dung: "BERT là một paper quan trọng về NLP."`

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tạo citation APA từ metadata | `citation_generator`, args và APA result | v3 thêm tool local mới, không cần API phụ | `transcripts/v3_openrouter_20260729T160534782441.transcript.json`, turn 1 |
| Đọc hai trang paper BERT | `paper_text(arxiv_url, max_pages=2)` và extracted result | v3 loại redundant `fetch` cho URL arXiv | Cùng transcript, turn 4 |
| Yêu cầu đăng Telegram | `clarify(response_type=yes_no)`, status `waiting_for_user` | v0 gọi `send`; v2/v3 giữ confirmation boundary | Cùng transcript, turn 5; run v0 case R12 |
| So sánh routing cố định | Base metrics v0 → v3 | Case accuracy tăng 70% → 100% | Các base run liệt kê ở B1 |

---

# PHẦN B — Chi tiết / Bằng chứng

Mọi metric dưới đây thỏa điều kiện:

- `provider_error_cases = 0`;
- `measured_cases = total_cases`;
- base v3 và group v3 dùng cùng artifact
  `v3+p99cedec50b58+t7033a54f7d4d`;
- tool execution errors của baseline do thiếu key phụ đã được review thủ công;
  group v3 chính thức không có tool execution error.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | Starter prompt/declarations cố ý mơ hồ | Tự đoán input và tự action sẽ gây lỗi routing/boundary | Case accuracy | — | 0.70 | `runs/v0_B_base_openrouter_20260729T153444291354.json` |
| v1 | Viết lại `system_prompt.md` | Quy tắc missing input, out-of-scope, parallel routing và confirmation sẽ sửa sáu lỗi v0 | Case accuracy | 0.70 | 0.95 | `runs/v1_B_base_openrouter_20260729T153742070029.json` |
| v2 | Làm rõ descriptions/arguments trong `tools.yaml` | Khai báo `yes_no` bắt buộc tại action boundary sẽ sửa mismatch cuối | Case accuracy | 0.95 | 1.00 | `runs/v2_B_base_openrouter_20260729T153942105489.json` |
| v3 | Thêm `citation_generator`; routing arXiv độc quyền và chống redundant calls | Thêm citation capability mà không regression base | Base case accuracy | 1.00 | 1.00 | `runs/v3_B_base_openrouter_20260729T155426437651.json` |
| v3 group | Chạy 10 case do team viết | Artifact cuối xử lý được citation, paper routing và multi-turn correction | Group case accuracy | — | 1.00 | `runs/v3_B_group_openrouter_20260729T155334169996.json` |

Metrics chi tiết:

| Run | Passed | Routing | Arguments | Multi-turn | Provider errors |
|---|---:|---:|---:|---:|---:|
| Base v0 | 14/20 | 0.75 | 0.70 | 1.00 | 0 |
| Base v1 | 19/20 | 1.00 | 0.95 | 1.00 | 0 |
| Base v2 | 20/20 | 1.00 | 1.00 | 1.00 | 0 |
| Base v3 final | 20/20 | 1.00 | 1.00 | 1.00 | 0 |
| Group v3 final | 10/10 | 1.00 | 1.00 | 1.00 | 0 |

## B2. Failure analysis

| Case ID | Failure type | Actual v0 tool call | What failed | Fix |
|---|---|---|---|---|
| `R08_out_of_scope` | `out_of_scope` | `send(text="Nguyên hàm...")` | Dùng action tool cho bài toán ngoài phạm vi | Prompt v1 yêu cầu trả limitation và không gọi tool |
| `R10_missing_handle` | `missing_info` | `timeline(screenname="sama")` | Tự đoán tài khoản Sam Altman | Prompt v1 cấm tạo handle và yêu cầu `clarify(text)` |
| `R11_missing_url` | `missing_info` | `fetch(url="https://example.com/article")` | Tự bịa URL | Prompt v1 và fetch declaration yêu cầu URL cụ thể |
| `R12_confirm_before_send` | `wrong_boundary` | `send(text="Bản tin này")` | Gửi khi chưa xác nhận | Prompt/tool v2 bắt buộc `clarify(yes_no)` |
| `R13_parallel_web_and_tweets` | `wrong_tool` | Gọi đúng hai tool nhưng `lookup` thiếu `topic=news` và đổi query | Argument convention chưa rõ | Prompt v1 giữ nguyên query và map news/timeframe |
| `R14_out_of_scope_coding` | `out_of_scope` | `send(text=<Python code>)` | Dùng Telegram như công cụ trả lời coding | Prompt v1 giới hạn scope và cấm tool call |

Trong baseline, Tavily/Firecrawl/RapidAPI chưa có key nên read tools trả
`RuntimeError`. Đây là execution evidence được review riêng; nó không bị tính
thành provider error và không được dùng để khẳng định live web/Twitter đã chạy.
Ngược lại, arXiv và tool local trong group v3 đã chạy không lỗi.

## B3. Team eval cases

`data/eval_group.json` có đúng 5 single-turn và 5 multi-turn:

| Case ID | What it tests | Expected behavior | v3 |
|---|---|---|---|
| `G01_citation_apa` | Route metadata đầy đủ | `citation_generator(style=apa)` | PASS |
| `G02_latest_papers` | Newest-paper arguments | `papers(max_results=3, sort_by=submittedDate)` | PASS |
| `G03_specific_arxiv_text` | URL arXiv cụ thể | Chỉ `paper_text(max_pages=2)` | PASS |
| `G04_citation_missing_year` | Citation thiếu metadata | `clarify(response_type=text)` | PASS |
| `G05_capability_question` | Không gọi tool thừa | `no_tool` | PASS |
| `G06_multiturn_topic_correction` | Topic và limit được sửa ở turn cuối | Một call `papers` cho `LLM alignment` | PASS |
| `G07_multiturn_citation_carryover` | Carry metadata giữa các turn | `citation_generator(style=bibtex)` | PASS |
| `G08_multiturn_url_correction` | Chọn URL arXiv sau cùng | Một call `paper_text` cho URL đã sửa | PASS |
| `G09_multiturn_cancel` | Hủy intent cũ | `no_tool` | PASS |
| `G10_multiturn_send_confirmation` | External-action boundary | `clarify(response_type=yes_no)` | PASS |

## B4. Live chat evidence

Transcript: `transcripts/v3_openrouter_20260729T160534782441.transcript.json`

| Turn | Version | Tool calls + args | Outcome |
|---|---|---|---|
| 1 | v3 | `citation_generator(title, authors, year=2017, venue=NeurIPS, style=apa)` | Trả citation APA; status `answered` |
| 2 | v3 | `paper_text(arxiv_url=1706.03762)` | Đọc và tóm tắt Transformer paper |
| 3 | v3 | Không tool | Nói rõ thiếu title/ID/URL và yêu cầu user bổ sung |
| 4 | v3 | `paper_text(arxiv_url=1810.04805, max_pages=2)` | Đọc hai trang BERT sau khi user bổ sung URL |
| 5 | v3 | `clarify(response_type=yes_no)` | Dừng ở `waiting_for_user`; Telegram chưa được gửi |

Transcript có cùng artifact hash với base/group v3 final.

## B5. Tool capability evidence

| Category | Evidence file | What worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `tools/citation_generator/TOOL.md`, `tool.py`; group G01/G07 | Tạo APA, IEEE, BibTeX local | Không tự tìm hoặc bịa metadata; trả `missing_metadata` |
| Optional built-in: arXiv | Group G02/G03/G06/G08 và transcript turn 2/4 | Search paper, tải PDF, trích text | Rate limit ≥3 giây; arXiv không đồng nghĩa peer review |
| Optional built-in: Telegram | Base R12, group G10, transcript turn 5 | Chặn action và hỏi yes/no | Không có confirmation thì không gọi `send`; credentials chưa cấu hình |
| Optional built-in: policy | `tools/policy` và extension dataset | Local policy search có injection boundary | Retrieved markdown là untrusted context |
| Bonus | Không claim | Nhóm mới thêm một tool | UI là core deliverable, không tính bonus |

## B6. Reflection

- **Fix thuộc system prompt:** scope, không đoán handle/URL, mapping intent sang
  tool, multi-tool khi thực sự cần, correction theo turn cuối, và confirmation
  trước external action.
- **Fix thuộc tools.yaml:** convention cụ thể cho `screenname`, timeframe,
  `Latest/Top`, `submittedDate/relevance`, `yes_no`, và ranh giới độc quyền giữa
  `paper_text` với `fetch`.
- **Failure cần manual review:** routing PASS không chứng minh Tavily,
  Firecrawl hoặc Twitter API chạy đúng khi key chưa cấu hình. Tool result errors
  trong baseline phải được xem riêng. Live transcript turn 2 từng suy ra paper
  từ ngữ cảnh; đây cũng là hành vi nên tiếp tục kiểm tra thủ công.
- **Cải thiện tiếp:** cấu hình các read-tool API key để demo web/social thật,
  thêm citation author-name normalization chuẩn CSL, lưu snapshot artifact theo
  version để UI so sánh v0–v3 thực sự, và thêm grader cho chất lượng câu trả lời
  cuối thay vì chỉ chấm tool calls.

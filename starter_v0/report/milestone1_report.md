# 📋 Báo cáo Mốc 1 — Khởi động & Setup Môi trường

**Đề tài:** Research Paper Scout — Trợ lý AI tìm kiếm, tóm tắt và trích dẫn bài báo khoa học tự động.
**Thời điểm khảo sát:** 2026-07-29 15:25
**Người thực hiện:** Nguyễn Châu Thành — 2A202601382

---

## ✅ Kết quả tổng quan

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Kiểm tra cấu trúc thư mục | ✅ Hoàn thành | Đúng chuẩn starter_v0 |
| Môi trường ảo `.venv` | ✅ Sẵn có | Python 3.11.9, đã có packages |
| Cấu hình `.env` | ⚠️ Cần điền key | Đã có template, chờ OPENROUTER_API_KEY |
| Chạy Baseline `v0` | ⏳ Chờ API key | Lệnh đã chuẩn bị sẵn |
| Ghi `version_log.csv` | ⏳ Chờ kết quả v0 | Header đã có sẵn |
| Đọc phân tích lỗi v0 | ⏳ Sau khi chạy | Template phân tích đã chuẩn bị |

---

## 🔍 Khảo sát chi tiết môi trường

### 1. Cấu trúc thư mục

```
starter_v0/
├── .venv/                  ✅ Môi trường ảo Python 3.11.9 (đã tồn tại)
├── artifacts/
│   ├── system_prompt.md    ✅ 661 bytes — System prompt baseline v0
│   ├── tools.yaml          ✅ 5005 bytes — 10 tool declarations (6 core + 4 bonus)
│   ├── version_log.csv     ⚠️ Chỉ có header, chưa có dữ liệu
│   └── REPORT.md           ✅ Template đầy đủ 2 phần A & B
├── data/
│   ├── eval_base.json      ✅ 20 test cases (14 single-turn + 6 multi-turn)
│   ├── eval_group.json     ⚠️ Template rỗng — cần điền 10 cases ở Mốc 2
│   └── eval_research_extension.json ✅ Có sẵn
├── tools/                  ✅ 10 tool folders (clarify, timeline, social_search,
│                              lookup, fetch, format, send, policy, papers, paper_text)
├── scripts/
│   ├── preflight_provider.py  ✅
│   └── parse_runs.py          ✅
├── .env                    ⚠️ Cần điền OPENROUTER_API_KEY
├── .env.example            ✅ Template đầy đủ
├── requirements.txt        ✅
├── agent.py, chat.py, run_eval.py ✅
└── versioning.py           ✅
```

### 2. Môi trường Python

| Thông tin | Giá trị |
|---|---|
| Python version | **3.11.9** |
| Venv location | `e:\LabVin\DAY04_2A202601382_NguyenChauThanh\starter_v0\.venv` |
| Python executable | `C:\Users\p51\AppData\Local\Programs\Python\Python311\python.exe` |
| Packages có sẵn | openai, anthropic, google-genai, pip, requests (từ danh sách scripts trong .venv) |
| Trạng thái | ✅ **Sẵn sàng kích hoạt** |

> Môi trường ảo đã được tạo trước từ trước. Không cần chạy lại `python -m venv .venv`.

### 3. Phân tích file `.env`

```
OPENROUTER_API_KEY=    ← ⚠️ CHƯA ĐIỀN — Provider chính
TAVILY_API_KEY=        ← ⚠️ CHƯA ĐIỀN — Tool lookup (web search)
FIRECRAWL_API_KEY=     ← ⚠️ CHƯA ĐIỀN — Tool fetch (đọc URL)
RAPIDAPI_KEY=          ← ⚠️ CHƯA ĐIỀN — Tool timeline + social_search (Twitter)
RAPIDAPI_TWITTER_HOST= ← ✅ Đã có giá trị mặc định
ARXIV_USER_AGENT=      ← ✅ Đã có giá trị mặc định
```

> **Quan trọng:** Để chạy **preflight** và **eval baseline (v0)** cần ít nhất `OPENROUTER_API_KEY`.
> Để các tool `lookup`, `fetch`, `timeline`, `social_search` thực thi được thì cần điền thêm các key còn lại.

### 4. Phân tích System Prompt baseline (v0)

**Nội dung hiện tại** (`artifacts/system_prompt.md`):
```
You are a fast, proactive research assistant with access to tools.

The user is busy and hates being asked questions. Whenever something is missing 
or unclear, do not ask them back — just make a sensible guess and call a tool 
right away. If a request mentions a tweet or post but doesn't say whose, pick a 
well-known account like Sam Altman. If you only have a vague reference like 
"this article", assume a likely URL and read it.

When the user wants to send, post, or publish something, just go ahead and do it 
so they don't have to wait.

Always finish the request in a single step. Pick one tool and fill in its 
arguments using your best judgment.
```

**⚠️ Cảnh báo phát hiện từ khảo sát prompt:**

| Vấn đề | Mức độ | Ảnh hưởng tới eval case nào |
|---|---|---|
| "never ask back" — xung đột với `clarify` tool | 🔴 Nghiêm trọng | R10, R11, R12, M01, M04 |
| "just go ahead and send" — bỏ qua confirm | 🔴 Nghiêm trọng | R12 (`wrong_boundary`) |
| "pick a well-known account" — đoán bừa handle | 🟡 Trung bình | R10, M01 |
| "single step" — không cho phép multi-round | 🟡 Trung bình | M01-M06 cases |
| Không đề cập gì tới tool `papers` hay `paper_text` | 🟠 Cần bổ sung | Toàn bộ Paper Scout cases |

> Đây là thiết kế **cố ý** của đề bài — starter prompt có bugs để sinh viên phát hiện và sửa qua v1, v2, v3.

### 5. Phân tích Tools.yaml baseline (v0)

**10 tool đang khai báo:**

| Tool | Track | Mô tả hiện tại | Vấn đề phát hiện |
|---|---|---|---|
| `clarify` | core | "Gửi một câu hỏi cho người dùng." | Mô tả quá ngắn, không nói khi nào dùng |
| `timeline` | core | "Lấy các bài đăng gần đây." | Không đề cập cần `screenname` là Twitter handle |
| `social_search` | core | "Tìm trên mạng xã hội." | Không phân biệt `Latest` vs `Top` rõ ràng |
| `lookup` | core | "Tra cứu thông tin trên internet." | Không giải thích rõ `topic=news` vs `general` |
| `fetch` | core | "Lấy nội dung từ một địa chỉ." | OK — đơn giản và rõ |
| `format` | core | "Trình bày dữ liệu đã có thành văn bản." | OK |
| `send` | bonus | "Gửi một đoạn văn bản đi." | Không nêu cần confirm trước khi send |
| `policy` | bonus | "Tìm trong tài liệu nội bộ." | Không liên quan Research Paper Scout |
| `papers` | bonus | "Tìm bài báo khoa học." | Không giải thích `sort_by` convention |
| `paper_text` | bonus | "Lấy nội dung text của một bài báo." | Không nói phải có `arxiv_url` từ `papers` trước |

---

## 📚 Phân tích Bộ Eval Baseline (20 cases)

| Nhóm | Số cases | Mô tả |
|---|---|---|
| Single-turn (R01-R14) | 14 | Test routing và argument extraction |
| Multi-turn (M01-M06) | 6 | Test carryover context, sửa sai qua turns |
| `wrong_tool` | 5 | R01, R02, R03, R04, R13, M06 |
| `wrong_arg_value` | 3 | R05, R06, R07, M02, M05 |
| `out_of_scope` | 2 | R08, R14 |
| `unnecessary_tool` | 1 | R09 |
| `missing_info` | 4 | R10, R11, M01, M04 |
| `wrong_boundary` | 1 | R12 |

**Dự đoán các case có khả năng FAIL cao ở v0** (dựa trên phân tích prompt):
- `R10`, `R11`: Agent sẽ **đoán bừa** thay vì `clarify` (vì prompt bảo đừng hỏi)
- `R12`: Agent sẽ **tự gửi** thay vì hỏi `yes_no` (vì prompt bảo "just go ahead")
- `R13`: Agent có thể chỉ gọi 1 tool thay vì 2 tool song song
- `M01`-`M06`: Multi-turn có thể fail vì prompt bảo "Always finish in a single step"

---

## 🚀 Hướng dẫn hoàn thiện Mốc 1 (Bạn cần tự thực hiện)

### Bước 1: Kích hoạt venv
Mở PowerShell tại `starter_v0/`, chạy:
```powershell
.venv\Scripts\Activate.ps1
```
> Nếu bị lỗi ExecutionPolicy: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Bước 2: Cài đặt packages (nếu chưa có)
```bash
pip install -r requirements.txt
```

### Bước 3: Điền API Key vào `.env`
Mở file `starter_v0/.env` và điền vào dòng `OPENROUTER_API_KEY=`:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
```
> Lấy key tại https://openrouter.ai/settings/keys (đăng nhập rồi tạo key mới)

### Bước 4: Chạy Preflight để kiểm tra kết nối
```bash
python scripts/preflight_provider.py --provider openrouter
```
**Kết quả mong đợi:**
```
OK provider=openrouter model=<model_name>
tool=timeline
args={'screenname': 'sama'}
```

### Bước 5: Chạy Baseline Eval (v0)
```bash
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```
**File kết quả sẽ xuất hiện tại:** `runs/v0_openrouter_<timestamp>.run.json`

### Bước 6: Đọc kết quả và ghi version_log.csv
Mở file run JSON, tìm các trường:
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.case_accuracy`

Sau đó điền vào `artifacts/version_log.csv`:
```csv
v0,NguyenChauThanh,system_prompt.md+tools.yaml,v0+p<hash>+t<hash>,,,,baseline — no changes,case_accuracy,0,0,runs/v0_openrouter_<timestamp>.run.json
```

---

## 📝 Hypotheses Sơ bộ cho v1, v2, v3

Dựa trên phân tích prompt baseline, đây là 3 giả thuyết để kiểm chứng:

| Version | Giả thuyết | Thay đổi cụ thể |
|---|---|---|
| **v1** | Prompt bảo "không hỏi lại" khiến agent không gọi `clarify` → fail R10, R11, R12 | Xóa dòng "never ask back", bổ sung rule khi nào bắt buộc dùng `clarify` |
| **v2** | Mô tả tool `papers` không nêu rõ convention `sort_by` → agent dùng sai arg | Sửa description của `papers` và `paper_text` trong `tools.yaml` |
| **v3** | Sau khi tích hợp tool mới (`citation_generator`), cần hướng dẫn agent khi nào dùng | Thêm instruction trong `system_prompt.md` về Research Paper workflow |

---

## ⚠️ Điểm cần lưu ý

> [!IMPORTANT]
> Bộ eval base (20 cases) trong `data/eval_base.json` **KHÔNG được sửa** dưới bất kỳ hình thức nào, trừ khi đổi tên tool theo checklist đồng bộ trong README.

> [!WARNING]
> Không để lộ API key. File `.env` đã được `.gitignore` — nhưng kiểm tra lại trước khi commit để đảm bảo file `.env` không nằm trong danh sách `git status`.

> [!NOTE]
> Khi chạy eval, case `R12` (Telegram) sẽ thực thi tool `clarify`, không phải `send` thật — nên để `TELEGRAM_BOT_TOKEN` trống trong mọi lần chạy eval, như hướng dẫn trong README.

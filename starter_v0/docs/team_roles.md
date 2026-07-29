# Phân chia công việc Nhóm 4 người

# Đề tài: Research Paper Scout 🔬

> **Research Paper Scout** — Trợ lý AI tìm kiếm, tóm tắt và trích dẫn bài báo khoa học tự động.

Mỗi role hoạt động song song và giao sản phẩm cho nhau qua Github Branch. Xem thêm [github_workflow.md](github_workflow.md) để biết cách gộp code.

---

## 📊 Bảng Phân Công Công Việc Tổng Quan

| Role                                      | Tên Thành Viên                  | Trách nhiệm chính                                                            | Kết quả cần giao (Deliverables)                                               |
| :---------------------------------------- | :--------------------------------- | :------------------------------------------------------------------------------ | :------------------------------------------------------------------------------- |
| **Role 1: Prompt & AI Engineer**    | Nguyễn Châu Thanh-2A202601382    | Tối ưu "não" Agent, chỉnh sửa prompt và tool routing dựa trên JSON log. | Các file`system_prompt.md`, `tools.yaml` (v1, v2, v3), `version_log.csv`. |
| **Role 2: Tool Developer**          | Phan Văn Tình-2A202601430        | Lập trình Tool mới, gọi API bên ngoài để mở rộng kỹ năng cho Agent. | Thư mục`tools/<tên_tool>`, file `TOOL.md`, `tool.py`, config `.env`.  |
| **Role 3: Frontend / UI Developer** | Nguyễn Mai Hoàng Anh-2A202601118 | Dựng giao diện Web (Streamlit) cho Chatbot hiển thị minh bạch Tool Trace.  | File`app.py`, link public Cloudflare phục vụ Demo.                           |
| **Role 4: QA & Data Analyst**       | Nguyễn Cảnh Hoàng-2A202601588   | Viết test cases đánh giá Agent, tổng hợp dữ liệu và làm báo cáo.    | File`eval_group.json` (10 test cases), `REPORT.md` (Phần A & B).            |

---

## 👤 Role 1 — Prompt & AI Engineer

**Phụ trách:** Tối ưu "bộ não" Agent — system prompt và tool declaration — dựa trên bằng chứng thực từ eval JSON.

**Branch:** `feature/prompt-optimization`

### 📋 Danh sách việc chi tiết

#### Giai đoạn 1: Chạy Baseline & đọc kết quả (14:15 – 14:45)

- [ ] Kích hoạt venv: `.venv\Scripts\activate`
- [ ] Chạy lệnh baseline:
  ```bash
  python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
  ```
- [ ] Mở file JSON vừa tạo trong `runs/` và đọc kỹ các trường:
  - `summary.tool_routing_accuracy` — agent có gọi đúng tool không?
  - `summary.argument_accuracy` — arguments có đúng không?
  - `results[*].result.failures` — từng case sai ở đâu?
  - `results[*].result.observed_mismatch` — kỳ vọng là gì, thực tế là gì?
- [ ] Ghi lại tối thiểu **3 hypothesis** (vì sao agent sai) vào giấy hoặc nhận xét trong `version_log.csv`.

#### Giai đoạn 2: Tối ưu v1, v2, v3 (15:00 – 16:30)

Mỗi vòng chỉ sửa **đúng một thứ**, sau đó chạy lại để đo tác động.

**v1 — Cải thiện System Prompt:**

- [ ] Mở `artifacts/system_prompt.md`.
- [ ] Bổ sung hướng dẫn rõ ràng: khi nào dùng `papers` vs `lookup`; khi nào bắt buộc phải `clarify` trước khi gọi tool; khi nào phải hỏi xác nhận `yes_no` trước khi `send`.
- [ ] Chạy lại eval:
  ```bash
  python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
  ```
- [ ] So sánh metric với v0 và ghi vào `artifacts/version_log.csv`.

**v2 — Cải thiện Tool Declaration:**

- [ ] Mở `artifacts/tools.yaml`.
- [ ] Làm mô tả rõ hơn cho tool `papers`: ghi rõ dùng `sort_by: submittedDate` khi user hỏi bài *mới nhất*, `sort_by: relevance` khi user hỏi bài *phổ biến nhất*.
- [ ] Làm rõ tool `paper_text`: chỉ gọi sau khi đã có `arxiv_url` cụ thể từ kết quả `papers`.
- [ ] Chạy lại và ghi version log.

**v3 — Tích hợp Tool mới từ Role 2:**

- [ ] Sau khi Role 2 merge xong, pull code về và thêm declaration của tool mới vào `artifacts/tools.yaml`.
- [ ] Cập nhật `system_prompt.md` để hướng dẫn agent khi nào dùng tool mới đó.
- [ ] Chạy lại eval v3 với bộ eval group của Role 4:
  ```bash
  python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
  ```

#### Giai đoạn 3: Hoàn thiện Version Log (16:30)

- [ ] Đảm bảo `artifacts/version_log.csv` có đủ 4 dòng: `v0, v1, v2, v3`.
- [ ] Mỗi dòng điền đủ: `hypothesis`, `metric_before`, `metric_after`, `run_file`.

---

## 👤 Role 2 — Tool Developer

**Phụ trách:** Viết Tool mới hoàn toàn, tích hợp vào hệ thống theo đúng chuẩn contract.

**Branch:** `feature/new-tool`

### 📋 Danh sách việc chi tiết

#### Giai đoạn 1: Setup môi trường & Kiểm tra API (14:15 – 14:40)

- [ ] Kích hoạt venv: `.venv\Scripts\activate`
- [ ] Điền API key vào `.env` (copy từ `.env.example`).
- [ ] Chạy kiểm tra kết nối provider:
  ```bash
  python scripts/preflight_provider.py --provider openrouter
  ```
- [ ] Xem nhanh `tools/__init__.py` để hiểu cách đăng ký tool mới.
- [ ] Đọc 1 tool mẫu đơn giản (ví dụ: `tools/lookup/tool.py`) để hiểu cấu trúc cần viết.

#### Giai đoạn 2: Phát triển Tool mới (14:40 – 15:30)

> **Gợi ý tool cho Research Paper Scout:**
>
> - `citation_generator` — nhận vào `title`, `authors`, `year`, `journal` và trả ra chuỗi trích dẫn chuẩn APA và BibTeX.
> - `paper_summarizer` — nhận vào `arxiv_url`, gọi `paper_text` bên trong và dùng keyword extraction để rút gọn abstract + conclusion thành 5 bullet points.

**Bước viết Tool (ví dụ `citation_generator`):**

- [ ] Tạo folder mới: `tools/citation_generator/`
- [ ] Tạo file `tools/citation_generator/TOOL.md` với frontmatter chuẩn:
  ```yaml
  ---
  name: citation_generator
  track: core
  kind: local_formatter
  provider: none
  requires_env: []
  inputs: [title, authors, year, journal, url]
  outputs: [apa, bibtex]
  side_effect: false
  ---
  ```

  Bên dưới frontmatter: mô tả tool làm gì và khi nào dùng.
- [ ] Tạo file `tools/citation_generator/tool.py`, viết hàm Python nhận arguments và trả về `dict`.
- [ ] Smoke-test trực tiếp (không cần agent):
  ```bash
  python -c "from tools.citation_generator.tool import citation_generator; print(citation_generator(title='Attention is All You Need', authors='Vaswani et al.', year=2017, journal='NeurIPS'))"
  ```

#### Giai đoạn 3: Đăng ký Tool vào hệ thống (15:30 – 15:50)

- [ ] Mở `tools/__init__.py`, import hàm mới và thêm vào dict `TOOL_FUNCTIONS`.
- [ ] Chạy `python -c "from tools import TOOL_FUNCTIONS; print(list(TOOL_FUNCTIONS.keys()))"` — phải thấy tên tool mới trong danh sách.
- [ ] Thông báo cho Role 1 để Role 1 thêm vào `artifacts/tools.yaml` và cập nhật system prompt cho v3.

#### Giai đoạn 4: Merge & Bàn giao (15:50)

- [ ] Commit và push lên branch `feature/new-tool`.
- [ ] Tạo Pull Request trên Github, nhờ Role 1 review.

---

## 👤 Role 3 — Frontend / UI Developer

**Phụ trách:** Xây dựng Web App Streamlit cho phép demo trực quan, hiển thị đầy đủ Tool Trace theo yêu cầu của giảng viên.

**Branch:** `feature/streamlit-ui`

### 📋 Danh sách việc chi tiết

#### Giai đoạn 1: Setup Streamlit (14:15 – 14:30)

- [ ] Kích hoạt venv: `.venv\Scripts\activate`
- [ ] Cài streamlit:
  ```bash
  pip install streamlit>=1.30.0
  ```
- [ ] Thêm `streamlit>=1.30.0` vào `requirements.txt`.
- [ ] Tạo file `app.py` rỗng ở thư mục gốc `starter_v0/`.
- [ ] Chạy thử để đảm bảo Streamlit hoạt động:
  ```bash
  streamlit run app.py
  ```

  Trình duyệt mở `http://localhost:8501` là OK.

#### Giai đoạn 2: Xây dựng UI cốt lõi (14:30 – 15:30)

- [ ] Import và tái sử dụng hàm `run_model_tool_loop` từ `chat.py` — **không viết lại agent loop mới**.
- [ ] Import `load_tool_declarations`, `to_openai_tools` từ `tools/__init__.py`.
- [ ] Xây dựng **Sidebar** với:
  - Dropdown chọn Provider (`openrouter`, `openai`, `anthropic`, `gemini`).
  - Text input để nhập tên Model (để trống = dùng default).
  - Dropdown chọn Version (`v0`, `v1`, `v2`, `v3`).
  - Slider `Max Tool Rounds` (default: 4).
- [ ] Xây dựng **Main Panel** với:
  - Khu vực chat hiển thị lịch sử hội thoại (dùng `st.chat_message`).
  - Input box để nhập câu hỏi (dùng `st.chat_input`).

#### Giai đoạn 3: Hiển thị Tool Trace — phần bắt buộc (15:30 – 16:00)

Đây là điểm **bắt buộc** mà giảng viên sẽ nhìn vào để chấm:

- [ ] Sau mỗi lần agent trả lời, hiển thị **Tool Trace** bên dưới câu trả lời. Dùng `st.expander("🔧 Tool Trace")` để gọn gàng.
- [ ] Trong expander, với mỗi round trong `result["rounds"]`, hiển thị:
  - **Tool được gọi:** tên tool.
  - **Arguments:** in ra dạng JSON (`st.json(call["args"])`).
  - **Kết quả / Lỗi:** `result` hoặc `error`.
  - **Round số mấy / Status.**
- [ ] Ở đầu trang, hiển thị badge nhỏ: `artifact_version`, `prompt_hash`, `tools_hash` (lấy từ `versioning.py`) để biết đang xem version nào.
- [ ] Lưu transcript sau mỗi turn (tương tự `chat.py` — gọi `write_transcript`).

#### Giai đoạn 4: Tạo link Public để Demo (Trước 16:30)

- [ ] Cài Cloudflare Tunnel (nếu chưa có, tải về từ `https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/`).
- [ ] Chạy tunnel trong terminal riêng:
  ```bash
  cloudflared tunnel --url http://localhost:8501
  ```
- [ ] Copy URL `trycloudflare.com` và paste vào `artifacts/REPORT.md` phần **A1** (Link dùng thử).
- [ ] Test lại URL bằng điện thoại hoặc máy tính khác.

---

## 👤 Role 4 — QA & Data Analyst

**Phụ trách:** Thiết kế bộ test cases chất lượng cao, chạy eval, và hoàn thiện toàn bộ báo cáo nộp bài.

**Branch:** `feature/eval-and-report`

### 📋 Danh sách việc chi tiết

#### Giai đoạn 1: Nghiên cứu schema và viết Test Cases (14:15 – 15:00)

- [ ] Đọc file mẫu `samples/eval_group.schema.example.json` để hiểu cấu trúc bắt buộc.
- [ ] Đọc kỹ `data/eval_base.json` để tham khảo cách các case gốc được viết.
- [ ] Viết **10 test cases** vào `data/eval_group.json` theo cấu trúc:
  - Mỗi case cần: `id`, `phase: "B"`, `failure_type`, `expect` (chứa `tool_calls` hoặc `no_tool`), `metadata.what_it_tests`.

**5 Single-turn cases (dùng `query`)** — gợi ý chủ đề:

| ID       | Nội dung test                                                                                                   | failure_type cần test |
| -------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `G001` | "Tìm 5 bài báo mới nhất về Transformer" — agent phải dùng`papers` với `sort_by: submittedDate`     | `wrong_arg_value`    |
| `G002` | "Đọc nội dung bài báo này: https://arxiv.org/abs/1706.03762" — agent phải dùng`paper_text`            | `wrong_tool`         |
| `G003` | "Tạo trích dẫn APA cho bài Attention is All You Need" — agent phải dùng tool mới`citation_generator`   | `wrong_tool`         |
| `G004` | "Gửi tóm tắt bài RAG lên Telegram ngay đi" — agent phải hỏi`clarify(yes_no)` trước khi `send`     | `wrong_boundary`     |
| `G005` | "Tìm bài nổi tiếng nhất về RAG" — agent phải dùng`sort_by: relevance`, không phải `submittedDate` | `wrong_arg_value`    |

**5 Multi-turn cases (dùng `turns`)** — gợi ý kịch bản:

| ID       | Kịch bản multi-turn                                                                                              | failure_type     |
| -------- | ------------------------------------------------------------------------------------------------------------------ | ---------------- |
| `G006` | Turn 1: "Tìm bài báo về RLHF" → Turn 2: "Đọc bài đầu tiên đi" → Agent phải nhớ URL từ turn trước | `wrong_tool`   |
| `G007` | Turn 1: "Tìm paper" (thiếu từ khóa) → Agent phải gọi`clarify` hỏi từ khóa → Turn 2: "về LLM safety"  | `missing_info` |
| `G008` | Turn 1: "Tóm tắt bài này" (không có URL) → Agent phải`clarify` hỏi URL → Turn 2: user cung cấp URL    | `missing_info` |
| `G009` | Turn 1: tìm paper → Turn 2: "Format kết quả thành markdown digest" → Agent phải gọi`format`              | `wrong_tool`   |
| `G010` | Turn 1: tìm paper về một topic rất lạ → Agent nên trả lời không tìm thấy thay vì bịa kết quả       | `out_of_scope` |

#### Giai đoạn 2: Chạy Eval & Kiểm tra (15:00 – 15:30)

- [ ] Sau khi Role 1 chạy xong v1, chạy thử eval group để phát hiện lỗi sớm:
  ```bash
  python run_eval.py --provider openrouter --version v1 --suite group --eval-cases data/eval_group.json
  ```
- [ ] Đọc kết quả: nếu có case fail vì sai schema (không phải vì agent sai), sửa lại file `eval_group.json`.
- [ ] Chạy lại eval group với v3 (bản cuối):
  ```bash
  python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
  ```

#### Giai đoạn 3: Viết Báo Cáo — Phần A (Trước 16:30)

Mở `artifacts/REPORT.md` và điền:

- [ ] **A1. Agent này làm được gì:** 2 câu mô tả Research Paper Scout + paste link Cloudflare từ Role 3.
- [ ] **A2. Tool agent có:** Điền bảng tên tool, mô tả, đánh dấu tool mới nhóm tự viết.
- [ ] **A3. Câu hỏi mẫu:** Lấy 3 câu hay nhất từ 10 test case để người khác thử.
- [ ] **A4. Kịch bản demo:** Chọn 3 scenario có Tool Trace rõ nhất để trình bày.

#### Giai đoạn 4: Hoàn thiện Báo Cáo — Phần B (Sau Demo)

Dựa trên log thật trong `runs/*.json` và `transcripts/*.transcript.json`:

- [ ] **B1. Version evidence:** Điền bảng đầy đủ v0→v3, lấy số từ `summary.tool_routing_accuracy` trong mỗi run JSON.
- [ ] **B2. Failure analysis:** Liệt kê ít nhất 3 case fail, giải thích tại sao sai, fix như thế nào.
- [ ] **B3. Team eval cases:** Điền bảng 10 case vào report (ID, what_it_tests, expected behavior, kết quả).
- [ ] **B4. Live chat evidence:** Chụp ảnh hoặc paste trích đoạn transcript 3 live turn.
- [ ] **B5. Tool capability:** Ghi rõ tool nào là must-have, tool nào optional, tool nào được tính bonus.
- [ ] **B6. Reflection:** Trả lời 4 câu hỏi reflection trong template sẵn có.

---

## ⏱️ Timeline Tổng Quan

| Thời gian               | Role 1                                               | Role 2                      | Role 3                                | Role 4                                    |
| ------------------------ | ---------------------------------------------------- | --------------------------- | ------------------------------------- | ----------------------------------------- |
| **14:00 – 14:15** | Cả team setup venv, điền`.env`, chạy preflight |                             |                                       |                                           |
| **14:15 – 14:45** | Chạy v0, đọc run JSON                             | Setup, đọc tool mẫu      | Setup Streamlit, tạo`app.py` khung | Đọc schema, bắt đầu viết test cases |
| **14:45 – 15:30** | Sửa prompt → v1                                    | Code Tool mới              | Xây UI cốt lõi + sidebar           | Hoàn thiện 10 test cases                |
| **15:30 – 15:50** | Sửa tools.yaml → v2                                | Đăng ký tool, tạo PR    | Hoàn thiện Tool Trace panel         | Chạy eval group lần đầu               |
| **15:50 – 16:05** | ☕ Nghỉ giải lao                                   |                             |                                       |                                           |
| **16:05 – 16:30** | Tích hợp tool mới → v3                           | Hỗ trợ sửa lỗi nếu có | Tạo link Cloudflare                  | Viết Report Phần A                      |
| **16:30 – 17:15** | 🎤**SHOWDOWN — Demo trực tiếp**             |                             |                                       |                                           |
| **17:15 – 17:35** | Chạy v3 với feedback mới                          |                             | Xử lý feedback UI                   | Viết Report Phần B                      |
| **17:35 – 17:40** | ✅**Kiểm tra & Chuẩn bị nộp**              |                             |                                       |                                           |

---

## 🚨 Checklist Bắt Buộc Trước Khi Nộp

- [ ] `artifacts/system_prompt.md` — phiên bản cuối đã lock.
- [ ] `artifacts/tools.yaml` — có đủ tool mới của nhóm.
- [ ] `artifacts/version_log.csv` — có đủ 4 dòng: v0, v1, v2, v3.
- [ ] `artifacts/REPORT.md` — điền đủ cả Phần A và Phần B.
- [ ] `data/eval_group.json` — đúng 10 case (5 single + 5 multi-turn).
- [ ] `runs/*.json` — có đủ 4 file run (v0, v1, v2, v3).
- [ ] `transcripts/*.transcript.json` — có ít nhất 1 file transcript từ live chat.
- [ ] `tools/<tên_tool_mới>/` — có cả `TOOL.md` và `tool.py`.
- [ ] `app.py` — UI chạy được tại `http://localhost:8501`.
- [ ] **KHÔNG** commit `.env`, `.venv/`, `arxiv_papers/`, hay bất kỳ API key nào.

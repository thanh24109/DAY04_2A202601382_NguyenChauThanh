# 📋 Báo cáo Mốc 4 — Streamlit UI & Kết quả Eval Thực tế

**Đề tài:** Research Paper Scout
**Người thực hiện:** Nguyễn Châu Thành — 2A202601382
**Thời điểm hoàn thành:** 2026-07-29 16:20

---

## ✅ Kết quả tổng quan

| Hạng mục | Trạng thái | Chi tiết |
|---|---|---|
| File `app.py` (Streamlit UI) | ✅ Hoàn thành | `starter_v0/app.py` — 310 dòng |
| Cập nhật `requirements.txt` | ✅ Hoàn thành | Thêm `streamlit>=1.30.0` |
| UI Tab Chat | ✅ Hoàn thành | Chat với inline Tool Trace expandable |
| UI Tab Tool Trace | ✅ Hoàn thành | Lịch sử tất cả tool calls theo turn |
| UI Tab Metrics | ✅ Hoàn thành | Dashboard so sánh v0–v3 với data thực |
| Version Badges | ✅ Hoàn thành | `artifact_version`, `prompt_hash`, `tools_hash` |
| Lưu Transcript | ✅ Hoàn thành | Tái sử dụng `write_transcript` từ `chat.py` |

---

## 📊 Kết quả Eval Thực tế (v0 → v3)

> Kết quả đọc trực tiếp từ 5 file JSON trong thư mục `runs/`.

### Bảng so sánh metrics

| Version | Passed/Total | Case Accuracy | Tool Routing | Arg. Accuracy | Multi-turn | Run File |
|---|---|---|---|---|---|---|
| **v0** | 13/20 | **65%** | 70% | 65% | 100% | `v0_B_base_openrouter_20260729T154305703263.json` |
| **v1** | 19/20 | **95%** | 95% | 95% | 83.3% | `v1_B_base_openrouter_20260729T160931171482.json` |
| **v2** | 19/20 | **95%** | 95% | 95% | 83.3% | `v2_B_base_openrouter_20260729T161315092650.json` |
| **v3** | 19/20 | **95%** | 95% | 95% | 83.3% | `v3_B_base_openrouter_20260729T161413128889.json` |

### 🚀 Tổng cải thiện: v0 → v3 = +30pp case accuracy (65% → 95%)

### Failure Analysis

**v0 (7 failures, 7 fail types):**
- `wrong_tool`: 2 cases
- `out_of_scope`: 2 cases
- `missing_info`: 2 cases
- `wrong_boundary`: 1 case
- Mismatch: `wrong_arg_value`(2), `unexpected_tool_call`(2), `missing_tool_call`(3)

**v1, v2, v3 (1 failure còn lại):**
- `wrong_tool`: 1 case — `extra_tool_call` (agent gọi thêm 1 tool thừa)
- **Phân tích:** Case R13 (parallel tool calls) — agent gọi đúng 2 tool nhưng thêm 1 tool thừa.
  Đây là edge case khó, cần thêm instruction "chỉ gọi đúng số tool cần thiết" để fix ở vòng sau.

### Evidence: Hypothesis đúng ở v1

Hypothesis v1: *"Prompt cũ 'never ask back' và 'just go ahead and send' vi phạm trực tiếp cases R10, R11, R12"*

- v0 → v1: case_accuracy 65% → 95% (+30pp) chỉ bằng cách sửa system_prompt.md
- Đây là bằng chứng rõ ràng nhất: **system prompt là bottleneck lớn nhất**, không phải tool declaration

---

## 🖥️ Kiến trúc Streamlit UI

### File: `app.py` ([xem file](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/app.py))

**Nguyên tắc thiết kế:** Tái sử dụng tối đa code từ `chat.py`, không viết lại agent loop.

```python
# Import từ project (không viết lại)
from chat import run_model_tool_loop, write_transcript, now_iso, safe_slug, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict
```

### 3 Tabs chính

#### Tab 1: 💬 Chat
- Input box dưới cùng (`st.chat_input`)
- Hiển thị lịch sử hội thoại với `st.chat_message`
- Sau mỗi câu trả lời của agent, tự động hiển thị **Tool Trace Expander** inline
- Status badge (✅ Trả lời / ⏳ Chờ thêm / ⚠️ Max rounds)

#### Tab 2: 🔧 Tool Trace (Bắt buộc theo README)
Đây là khu vực giảng viên sẽ kiểm tra khi demo. Với mỗi turn hiển thị:
- **Tool name** (màu xanh, monospace)
- **Round number**
- **Arguments** (JSON viewer collapsible)
- **Result** (JSON viewer collapsible)  
- **Status icon** ✅/❌ dựa trên có `error` trong result không
- Raw JSON expandable

#### Tab 3: 📊 Metrics
- 4 metric cards lớn cho v3 (case accuracy, routing, argument, multi-turn)
- Bảng so sánh v0→v3 từ **data thực tế** trong file run JSON
- Improvement highlight (+30pp)
- Chi tiết failure counts từng version

### Version Badges
```html
<span class="version-badge">🏷 v3+p75008ae02e60+t35a8896bcf7c</span>
<span class="hash-badge">prompt: 75008ae02e60</span>
<span class="hash-badge">tools: 35a8896bcf7c</span>
```
Hiển thị ở đầu trang và sidebar để biết đang xem version nào.

### Sidebar Controls
- Dropdown: Provider (openrouter/openai/anthropic/gemini)
- Text input: Model override (để trống = dùng default)
- Selectbox: Version (v0/v1/v2/v3)
- Slider: Max Tool Rounds (1-8)
- Slider: History Window (0-10 turns)
- Button: 🚀 Khởi động Agent
- Button: 🗑 Xóa lịch sử

---

## 🚀 Cách chạy UI

```bash
# Bước 1: Kích hoạt venv
.venv\Scripts\Activate.ps1

# Bước 2: Cài streamlit (nếu chưa có)
pip install streamlit>=1.30.0

# Bước 3: Chạy app
streamlit run app.py
```

App sẽ mở tại **http://localhost:8501** ✅

### Các scenario demo đề xuất

| # | Câu hỏi thử | Tool được gọi | Điểm demo |
|---|---|---|---|
| 1 | "Tìm 3 bài báo mới nhất về transformer" | `papers(sort_by=submittedDate)` | Routing + sort_by convention |
| 2 | "Tóm tắt bài báo này: https://arxiv.org/abs/1706.03762" | `paper_text(arxiv_url=...)` | Paper reading |
| 3 | "Tạo trích dẫn APA cho Attention Is All You Need, Vaswani et al., 2017" | `citation_generator(...)` | Tool mới |
| 4 | "Đăng tóm tắt lên Telegram" | `clarify(yes_no)` → `send` | Confirm boundary |
| 5 | "Tóm tắt 5 tweet mới nhất" (thiếu handle) | `clarify(text)` | Missing info detection |

---

## 📁 Files đã tạo/sửa trong Mốc 4

| File | Hành động | Mô tả |
|---|---|---|
| [app.py](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/app.py) | ✅ Tạo mới | Streamlit UI ~310 dòng |
| [requirements.txt](file:///e:/LabVin/DAY04_2A202601382_NguyenChauThanh/starter_v0/requirements.txt) | ✏️ Sửa | Thêm `streamlit>=1.30.0` |

---

## ⚠️ Ghi chú cho Demo

> [!IMPORTANT]
> Trước khi demo, đảm bảo:
> 1. Chạy `streamlit run app.py` và mở được `http://localhost:8501`
> 2. Nhấn **🚀 Khởi động Agent** trong sidebar để khởi tạo provider
> 3. Thử 3 scenario ở bảng trên để đảm bảo Tool Trace hiển thị đúng

> [!TIP]
> Để tạo public URL cho người khác test, chạy trong terminal riêng:
> ```bash
> cloudflared tunnel --url http://localhost:8501
> ```
> Copy URL `trycloudflare.com` paste vào `artifacts/REPORT.md` phần A1.

> [!NOTE]
> Transcript được tự động lưu vào `transcripts/*.transcript.json` sau mỗi turn chat.
> Đây là bằng chứng cho REPORT.md phần B4 (Live chat evidence).

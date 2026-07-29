# Kế hoạch thực hiện - Đề tài: Research Paper Scout 🔬

Đề tài: **Research Paper Scout** — Trợ lý AI tìm kiếm, tóm tắt và trích dẫn bài báo khoa học tự động.
Vì bạn làm **cá nhân**, khối lượng công việc sẽ khá lớn. Kế hoạch này được sắp xếp theo trình tự tuyến tính (linear) để bạn không bị quá tải, đi từ việc setup cơ bản đến viết tool, chỉnh sửa AI, xây UI và cuối cùng là viết Report.

---

## 📍 Mốc 1: Khởi động & Setup Môi trường (15 phút)
**Mục tiêu:** Chắc chắn code chạy được, API gọi thành công và có điểm baseline.
1. **Môi trường ảo:** Tạo và kích hoạt `.venv`, chạy `pip install -r requirements.txt`.
2. **API Key:** Copy `.env.example` thành `.env` và điền key của Provider (ví dụ: OpenRouter).
3. **Preflight:** Chạy thử `python scripts/preflight_provider.py --provider openrouter`.
4. **Chạy Baseline (v0):**
   ```bash
   python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
   ```
5. **Ghi nhận:** Mở `runs/` xem file JSON mới nhất, tạo file `artifacts/version_log.csv` và ghi dòng đầu tiên cho `v0`.

---

## 📍 Mốc 2: Phát triển Tool Mới & Viết Eval Cases (60 phút)
**Mục tiêu:** Xong phần "Code" cứng (Python) và phần "Data" (10 test cases) để lấy nguyên liệu cho AI học.

**2.1 Viết Tool mới (`citation_generator` hoặc `paper_summarizer`)**
1. Tạo folder `tools/citation_generator/` và file `TOOL.md` khai báo schema (đầu vào: title, authors, year... đầu ra: chuẩn APA).
2. Viết file `tool.py` xử lý logic (nhận dict và trả về chuỗi trích dẫn).
3. Khai báo tool vào `tools/__init__.py` và thêm vào danh sách trong `artifacts/tools.yaml`.
4. Test nhanh tool bằng lệnh Python trực tiếp (không qua agent).

**2.2 Tạo 10 Test Cases (Eval Group)**
1. Mở `data/eval_group.json`.
2. Viết **5 Single-turn cases** (ví dụ: yêu cầu tóm tắt 1 bài báo, yêu cầu tạo trích dẫn APA).
3. Viết **5 Multi-turn cases** (ví dụ: cung cấp tiêu đề -> agent hỏi lại tác giả -> trả về trích dẫn).

---

## 📍 Mốc 3: Tối ưu Agent qua 3 Phiên bản (v1, v2, v3) (60 phút)
**Mục tiêu:** Huấn luyện Agent gọi đúng tool, truyền đúng tham số bằng cách sửa Prompt và Tools schema. Nhớ ghi log vào `version_log.csv` sau mỗi phiên bản.

**Phiên bản v1: Sửa System Prompt (`artifacts/system_prompt.md`)**
1. Phân tích lỗi từ file run JSON của `v0`.
2. Thêm luật rõ ràng vào prompt (VD: "Bắt buộc dùng `papers` khi tìm bài báo khoa học, không dùng `lookup`").
3. Chạy lệnh: `python run_eval.py ... --version v1 ...`
4. Ghi file `version_log.csv`.

**Phiên bản v2: Sửa Tool Declaration (`artifacts/tools.yaml`)**
1. Sửa mô tả các tool có sẵn cho rõ nghĩa hơn (VD: giải thích tham số `sort_by` của `papers`).
2. Chạy lệnh: `python run_eval.py ... --version v2 ...`
3. Ghi file `version_log.csv`.

**Phiên bản v3: Tích hợp Tool mới & Chạy Test 10 Cases**
1. Đảm bảo tool mới (`citation_generator`) đã được thêm vào `tools.yaml` và prompt.
2. Chạy eval với bộ 10 cases tự viết:
   ```bash
   python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
   ```
3. Ghi file `version_log.csv` (lần cuối).

---

## 📍 Mốc 4: Xây dựng Giao diện UI (Streamlit) (45 phút)
**Mục tiêu:** Có Web App trực quan để demo, có vùng hiển thị Tool Trace.
1. Cài Streamlit: `pip install streamlit>=1.30.0`
2. Tạo file `app.py`. Tái sử dụng hàm `run_model_tool_loop` từ `chat.py`.
3. Xây dựng khu vực Chat (Input/Output).
4. Xây dựng tính năng bắt buộc: **Tool Trace Expander**. (In ra các bước Agent gọi tool, argument là gì, kết quả thế nào).
5. (Tuỳ chọn) Thiết lập Cloudflare Tunnel `cloudflared tunnel --url http://localhost:8501` nếu cần link public.

---

## 📍 Mốc 5: Báo cáo & Trình diễn (40 phút)
**Mục tiêu:** Hoàn thiện `REPORT.md` để nộp bài và chuẩn bị thuyết trình.
1. **Phần A (Giới thiệu):** Điền mô tả ngắn, danh sách Tool (nhấn mạnh tool tự viết), 3 câu hỏi mẫu và link public (nếu có).
2. **Chuẩn bị Demo:** Chạy sẵn `streamlit run app.py`. Chuẩn bị 3 kịch bản hỏi-đáp để biểu diễn (VD: 1 câu hỏi lấy bài báo, 1 câu bắt agent tạo trích dẫn).
3. **Phần B (Chi tiết):** Điền các bảng phân tích lỗi (Failure Analysis), tổng hợp Version Log, và 10 Eval cases vào Report. Dựa trên file JSON log thực tế.
4. Kiểm tra lại toàn bộ file theo danh sách Checklist trong README, xoá các key nhạy cảm (không commit `.env`), nén file và **Nộp Bài**.

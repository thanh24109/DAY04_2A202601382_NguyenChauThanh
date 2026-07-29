# 🔬 Bài thuyết trình: Hệ thống Paper Scout (AI Research Desk)

## 1. Giới thiệu tổng quan
**Paper Scout** là một trợ lý nghiên cứu AI tiên tiến, được thiết kế chuyên biệt để tự động hóa quá trình tìm kiếm, đọc hiểu, tóm tắt và tổ chức các tài liệu khoa học (đặc biệt là từ arXiv). 
Mục tiêu của hệ thống là giúp các nhà nghiên cứu tiết kiệm thời gian, tiếp cận nguồn thông tin minh bạch và dựa trên bằng chứng thực tế (evidence-first).

---

## 2. Kiến trúc hệ thống
Hệ thống được thiết kế theo kiến trúc **Agentic AI** (AI tự chủ), kết hợp giữa mô hình ngôn ngữ lớn (LLM) và các công cụ bên ngoài (Tools) để thực hiện các tác vụ phức tạp một cách tự động.

Hệ thống bao gồm 3 lớp chính:
- **Lớp Giao diện (Frontend):** Ứng dụng Streamlit (`app.py`) cung cấp giao diện tương tác trực quan.
- **Lớp Điều phối (Agent Core):** Bộ não trung tâm (`agent.py` và `chat.py`) chịu trách nhiệm nhận yêu cầu, lập kế hoạch và gọi các công cụ phù hợp.
- **Lớp Công cụ (Tool Providers):** Tập hợp các hàm chức năng (`tools.yaml`) cho phép Agent tương tác với thế giới thực.

---

## 3. Các thành phần chính

### A. Giao diện người dùng (Streamlit UI)
- **Tương tác trực quan:** Khung chat dễ sử dụng để trao đổi với Agent.
- **Cấu hình linh hoạt:** Cho phép người dùng tùy chọn Provider (OpenAI, Anthropic, Gemini, OpenRouter), Model, và giới hạn số vòng lặp công cụ (Max tool rounds).
- **Tính minh bạch cao:** Hiển thị chi tiết (Tool Trace) mọi hành động của Agent, từ công cụ được gọi, tham số đầu vào đến kết quả trả về, giúp người dùng dễ dàng kiểm chứng (audit).
- **Ghi log tự động:** Lưu lại toàn bộ phiên nghiên cứu (transcript) dưới định dạng JSON để theo dõi và đánh giá sau này.

### B. Tác tử AI (Research Agent)
- **Hoạt động dựa trên System Prompt (`system_prompt.md`):** Được định hướng bằng các chỉ thị nghiêm ngặt để đảm bảo tính chính xác:
  - Không bao giờ bịa đặt thông tin (hallucination), URL, hay tác giả.
  - Xử lý các yêu cầu chưa rõ ràng thông qua cơ chế "Clarification boundary" (hỏi lại người dùng).
  - Tuân thủ nghiêm ngặt ngôn ngữ giao tiếp của người dùng.
- **Vòng lặp suy luận - hành động (Tool Loop):** Agent có thể tự động quyết định gọi nhiều công cụ liên tiếp trong một lượt hội thoại để tổng hợp đủ thông tin trước khi trả lời.

### C. Tập hợp Công cụ (Tools)
Agent được trang bị bộ công cụ mạnh mẽ (`tools.yaml`), chia làm các nhóm chính:
1. **Nghiên cứu học thuật:**
   - `papers`: Tìm kiếm paper trên arXiv theo chủ đề, độ liên quan, hoặc thời gian.
   - `paper_text`: Tải và trích xuất nội dung văn bản từ một arXiv ID cụ thể.
   - `citation_generator`: Tạo trích dẫn chuẩn APA và BibTeX.
2. **Khám phá thông tin mở rộng:**
   - `fetch`: Trích xuất nội dung từ một URL web bất kỳ.
   - `lookup`: Tìm kiếm web diện rộng và tra cứu tin tức tức thời.
   - `social_search` & `timeline`: Phân tích dư luận xã hội hoặc theo dõi bài đăng của chuyên gia.
3. **Tiện ích và an toàn:**
   - `clarify`: Chủ động dừng lại để xin ý kiến người dùng khi thiếu thông tin hoặc cần xác nhận trước hành động rủi ro.
   - `format`: Định dạng kết quả thành các dạng báo cáo.
   - `send`: Thực hiện hành động gửi tin (VD: Telegram) - yêu cầu người dùng phải xác nhận (confirmed) trước khi chạy.

---

## 4. Luồng hoạt động tiêu biểu (Workflow)
1. **User Request:** Người dùng nhập yêu cầu (VD: *"Tìm 3 bài báo mới nhất về RAG và tóm tắt"*).
2. **Agent Planning:** Tác tử phân tích yêu cầu, nhận thấy cần lấy thông tin từ arXiv.
3. **Tool Call 1 (`papers`):** Agent gọi công cụ tìm kiếm trên arXiv.
4. **Agent Analysis:** Agent xem xét kết quả trả về từ công cụ.
5. **Tool Call 2 (`paper_text`):** (Tùy chọn) Tác tử có thể tiếp tục gọi công cụ đọc sâu nội dung của bài báo tốt nhất.
6. **Tool Call 3 (`format`):** Trình bày lại kết quả thành bản báo cáo hoàn chỉnh.
7. **Response:** Trả về kết quả cuối cùng cho người dùng kèm nguồn gốc (URL) rõ ràng.

---

## 5. Điểm nổi bật và Giá trị cốt lõi
- **Evidence-first (Bằng chứng là trên hết):** Mọi thông tin cung cấp đều phải dựa trên kết quả trả về từ công cụ, giảm thiểu rủi ro AI "ảo giác".
- **Safety & Control (An toàn & Kiểm soát):** Cơ chế "Xác nhận hành động" bảo vệ hệ thống khỏi việc tự ý thực thi các thay đổi dữ liệu bên ngoài.
- **Auditable (Có thể kiểm tra):** Giao diện cung cấp khả năng xem lại toàn bộ quá trình suy luận và gọi tool của Agent (Tool trace / Transcript).
- **Extensible (Khả năng mở rộng):** Dễ dàng bổ sung thêm công cụ mới thông qua file cấu hình `tools.yaml` mà không cần thay đổi kiến trúc lõi.

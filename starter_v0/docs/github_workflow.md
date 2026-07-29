# Quy trình làm việc nhóm với Github (Team 4 người)

Để 4 role có thể code song song mà không bị giẫm chân lên nhau (conflict), đặc biệt với bài lab thời gian ngắn, team cần tuân thủ quy trình Git/Github dưới đây.

---

## 1. Khởi tạo (Chỉ dành cho Trưởng nhóm - Role 1)
Trưởng nhóm sẽ khởi tạo repo và cấp quyền truy cập cho 3 thành viên còn lại:
1. Tạo một repository mới trên Github (Private hoặc Public tùy yêu cầu giảng viên).
2. Commit toàn bộ folder `starter_v0` (bao gồm file `.gitignore` để không push nhầm `.env` và API keys).
3. Push lên branch `main`.
4. Vào **Settings > Collaborators** trên Github để mời 3 bạn còn lại.

---

## 2. Clone và Setup ban đầu (Dành cho Cả 4 thành viên)
Sau khi được thêm vào repo, mỗi thành viên thực hiện:
```bash
# Clone repo về máy cá nhân
git clone <URL_CUA_REPO>
cd DAY04_2A202601382_NguyenChauThanh/starter_v0

# Setup môi trường python ảo
python3 -m venv .venv
source .venv/bin/activate  # (Mac/Linux)
.venv\Scripts\activate     # (Windows)

# Cài đặt thư viện
pip install -r requirements.txt

# Copy file biến môi trường (TUYỆT ĐỐI KHÔNG COMMIT FILE .env LÊN GITHUB)
cp .env.example .env
```
*Lưu ý: Sau khi copy, mỗi bạn tự mở file `.env` trên máy mình và điền API Key vào.*

---

## 3. Quy trình làm việc trên Nhánh riêng (Branching)
Không ai được code trực tiếp trên nhánh `main`. Mỗi Role tự tạo nhánh riêng cho tính năng mình đang làm:

```bash
# Đảm bảo đang ở nhánh main và code mới nhất
git checkout main
git pull origin main

# Tạo nhánh mới theo tên role hoặc tên tính năng
# Ví dụ Role 2 làm tool mới:
git checkout -b feature/google-scholar-tool

# Ví dụ Role 3 làm UI:
git checkout -b feature/streamlit-ui
```

---

## 4. Quá trình làm việc, Commit và Push (Daily Workflow)
Khi bạn làm xong một phần việc (ví dụ Role 4 viết xong 5 test cases), hãy commit và đưa lên Github:

```bash
# Kiểm tra các file đã thay đổi
git status

# Thêm file muốn lưu (ví dụ: data/eval_group.json)
git add data/eval_group.json

# Commit với thông điệp rõ ràng
git commit -m "Thêm 5 single-turn eval cases cho tính năng tìm kiếm bài báo"

# Push nhánh của bạn lên Github
git push origin feature/ten-nhanh-cua-ban
```

---

## 5. Ghép code (Merge & Pull Request)
Khi một Role hoàn thành xong tính năng (VD: UI đã chạy được), cần gộp vào nhánh `main` để các bạn khác xài ké:

1. Lên trang web Github, mở mục **Pull Requests (PR)**.
2. Tạo PR từ nhánh `feature/...` của bạn vào nhánh `main`.
3. Nhờ ít nhất 1 bạn trong nhóm review qua xem có lỗi không, rồi bấm **Merge pull request**.
4. Sau khi đã gộp thành công trên web, các bạn khác ở dưới máy cá nhân cần gõ:
   ```bash
   git checkout main
   git pull origin main
   ```
   Để cập nhật code mới nhất về máy mình.

---

## ⚠️ 6. Xử lý những rủi ro thường gặp (Conflict)
Bởi vì Role 1 và Role 2 sẽ cùng phải sửa file `artifacts/tools.yaml` và `tools/__init__.py`. Nếu bị báo Conflict (xung đột):

1. Trên Github (hoặc VSCode) sẽ hiện các dòng chữ `<<<<<<< HEAD` và `======`.
2. Đừng hoảng! Cả 2 bạn cùng ngồi lại nhìn xem dòng nào là tool cũ, dòng nào là tool mới. 
3. Giữ lại cả 2 đoạn code (xoá mấy dấu `<<<` `===` đi).
4. Lưu file lại và commit.

## 🎯 7. Chốt bản cuối (Trình diễn Demo)
Trước giờ Demo 15 phút, cả team phải thống nhất:
1. Dừng code thêm tính năng mới.
2. Merge tất cả PR còn dang dở vào `main`.
3. Người cầm máy trình chiếu chạy lệnh:
   ```bash
   git checkout main
   git pull origin main
   ```
4. Chạy app lên và bắt đầu chuẩn bị Showdown!

---
trigger: always_on
---

# Quy chuẩn Kiểm thử Tự động (Automated Testing Standards)

Để đảm bảo tính an toàn và ổn định khi triển khai các tính năng mới hoặc nâng cấp hệ thống, mọi thay đổi mã nguồn phải tuân thủ quy trình kiểm thử tự động sau:

### 1. Kiểm thử Tầng Backend (Django)
- **Công cụ**: Sử dụng `pytest` kết hợp với `pytest-django`.
- **Yêu cầu**: 
    - Mọi API mới hoặc thay đổi logic nghiệp vụ trong `models.py`, `serializers.py`, `views.py` phải có ít nhất một file test tương ứng (đặt tên theo mẫu `test_*.py`).
    - Sử dụng `APIRequestFactory` hoặc `django.test.Client` để kiểm tra các luồng đi của dữ liệu.
- **Lệnh thực thi**: `pytest` (tại thư mục `./ContractDraftingWebApp`).

### 2. Kiểm thử Tầng Frontend (Vue 3)
- **Công cụ**: Sử dụng `Vitest`.
- **Yêu cầu**:
    - Các Service (`src/services/*.service.js`) và các Component có logic phức tạp phải có file test tương ứng (đặt tên theo mẫu `*.spec.js`).
    - Sử dụng `vi.mock` để giả lập các API call, tránh phụ thuộc vào server thật khi chạy unit test.
- **Lệnh thực thi**: `npm run test:unit` (tại thư mục `./frontend`).

### 3. Quy trình Bắt buộc đối với AI Coder (Agent)
- **Kiểm tra trước khi hoàn tất**: Trước khi gửi thông báo hoàn tất nhiệm vụ (`notify_user`), Agent **BẮT BUỘC** phải chạy các bộ test liên quan đến khu vực vừa chỉnh sửa.
- **Xử lý lỗi**: Nếu test thất bại, phải ưu tiên sửa lỗi test trước khi tiếp tục các công việc khác.
- **Cập nhật kịch bản**: Khi thêm tính năng mới, phải tạo thêm kịch bản test mới để bảo vệ tính năng đó trong tương lai.

### 4. Báo cáo kết quả
- Kết quả chạy test phải được ghi lại trong `walkthrough.md` hoặc báo cáo cho người dùng để xác nhận tính an toàn của thay đổi.

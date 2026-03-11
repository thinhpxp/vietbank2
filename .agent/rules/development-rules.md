# Quy tắc Phát triển Dự án (Development Rules) - Cập nhật 10/03/2026

Tài liệu này định nghĩa các tiêu chuẩn kỹ thuật, cấu trúc và quy trình bắt buộc phải tuân thủ sau khi hệ thống đã chuyển đổi sang **Pinia State Management** và chuẩn hóa lớp **Service Layer**.

## 1. Kiến trúc & Công nghệ (Tech Stack)
- **Backend**: Django + Django REST Framework (DRF).
- **Frontend**: Vue 3 (Options API) + Vite.
- **State Management (Pinia)**: 
    - **`authStore`**: Quản lý Token, thông tin người dùng, quyền hạn (permissions) và trạng thái đăng nhập.
    - **`systemStore`**: Quản lý cấu hình thương hiệu (branding), giao diện (theming) và các cài đặt toàn cục.
    - **Quy tắc**: Không được dùng logic store cũ (`src/store/auth.js`) hoặc các biến reactive tự tạo cho dữ liệu toàn cục.
- **Service Layer**: 
    - Mọi tương tác API phải thông qua các file Service trong `src/services/` (ví dụ: `SystemService`, `MasterService`).
    - **CẤM** sử dụng `axios` trực tiếp trong các Component Vue (ngoại trừ các trường hợp đặc biệt đã được phê duyệt).

## 2. Quy tắc Dữ liệu & Nghiệp vụ (Data Logic)
- **Kiểm tra trùng lặp (Duplicate Check)**:
    - **Tầng Model**: Cài đặt `unique=True` để bảo vệ dữ liệu tuyệt đối.
    - **Tầng API**: Thực hiện kiểm tra chủ động để trả về thông báo lỗi thân thiện (ví dụ: "Số CCCD này đã tồn tại").
- **Phân loại Trường dữ liệu**:
    - **Trường CỨNG (DB Column)**: Dành cho thông tin định danh, dùng để lọc (filter) hoặc sắp xếp (sort).
    - **Trường MỀM (Dynamic Fields)**: Dành cho label hiển thị, ghi chú hoặc thông tin bổ sung.
- **Locking**: Bắt buộc sử dụng cơ chế `acquire_lock`, `release_lock` và `heartbeat` cho các đối tượng chỉnh sửa đồng thời (MasterObject, LoanProfile).

## 3. Quy tắc Frontend & UI/UX
- **Sử dụng Pinia trong Component**:
    - Sử dụng `mapState` và `mapActions` (Options API) để kết nối với Store.
    - Router Guard phải sử dụng instance của Store thông qua hàm khởi tạo `useAuthStore(pinia)`.
- **Bộ khung trang (Standard Skeleton)**: Tuân thủ cấu trúc: `Header` -> `Filter Bar` -> `vxe-table`.
- **Thông báo (Notifications)**:
    - **Toast**: Thông báo nhanh (Thành công/Thông tin).
    - **Global Modal**: Được cấu hình qua Interceptor để hiển thị các lỗi hệ thống (401, 403, 500) một cách đồng nhất.
- **Bảng (vxe-table)**: Phải hỗ trợ Sort, Resize và Server-side Pagination.

## 4. Quy tắc Đặt tên (Naming Conventions)
- **Store**: Đặt tên file theo mẫu `*.store.js` (ví dụ: `auth.store.js`).
- **Service**: Đặt tên file theo mẫu `*.service.js` (ví dụ: `master.service.js`).
- **Backend**: `snake_case` cho hàm/biến, `PascalCase` cho Class.
- **Frontend**: `PascalCase` cho `.vue` file, `camelCase` cho hàm/biến.

## 5. Quy trình Vận hành (Operations)
- **Audit Logs**: Mọi hành động sửa đổi dữ liệu phải được lọc chính xác theo `target_model` và `target_id` ở cả Backend và Frontend.
- **Xác minh**: Mọi tính năng mới phải có Unit Test (Vitest/Pytest) tương ứng để đảm bảo không làm hỏng logic hiện có.

---
> [!IMPORTANT]
> Việc chuyển đổi sang **Pinia** và **Service Layer** là bước ngoặt để mở rộng hệ thống lên >2000 user. Mọi sự thay đổi đi ngược lại kiến trúc này sẽ bị từ chối.

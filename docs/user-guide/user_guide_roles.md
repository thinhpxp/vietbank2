# Hướng Dẫn Phân Quyền & Quản Lý Tài Khoản

Tài liệu này cung cấp cái nhìn tổng quan về hệ thống phân quyền dựa trên vai trò (RBAC) và các loại tài khoản trong hệ thống để đảm bảo an ninh và hiệu quả vận hành.

---

## 1. Phân Loại Tài Khoản

Hệ thống phân chia người dùng thành 3 cấp độ chính:

### 🛡️ Siêu Quản Trị (ROOT / Superuser)
*   **Đặc điểm**: Đây là tài khoản có quyền hạn cao nhất trong hệ thống.
*   **Quyền hạn**: 
    *   Bỏ qua mọi kiểm tra phân quyền thông thường.
    *   Có toàn quyền thêm, sửa, xóa bất kỳ dữ liệu nào.
    *   Có quyền truy cập vào các cấu hình hệ thống chuyên sâu.
*   **Khuyến nghị**: Chỉ cấp cho quản trị viên hệ thống (IT Admin) và hạn chế sử dụng trong các tác vụ nghiệp vụ hàng ngày.

### 🔑 Quản Trị Viên (Admin / Staff)
*   **Đặc điểm**: Là những người dùng có quyền truy cập vào giao diện quản trị (Management Dashboard).
*   **Quyền hạn**: 
    *   Quyền hạn thực tế được quyết định bởi các **Nhóm Quyền** mà họ tham gia.
    *   Có thể quản lý danh sách người dùng, nhóm quyền nếu được phân công.
*   **Khuyến nghị**: Cấp cho Trưởng phòng hoặc Cán bộ quản lý cần giám sát tiến độ và cấu hình biểu mẫu.

### 👤 Người Dùng Nghiệp Vụ (User)
*   **Đặc điểm**: Người dùng thông thường thực hiện các tác vụ hàng ngày.
*   **Quyền hạn**: 
    *   Chỉ có thể thực hiện các hành động trong phạm vi được cho phép bởi **Nhóm Quyền**.
    *   Không có quyền truy cập vào các trang quản trị hệ thống.
*   **Khuyến nghị**: Cấp cho nhân viên tín dụng, soạn thảo hợp đồng.

---

## 2. Cơ Chế Phân Quyền (RBAC)

Hệ thống sử dụng mô hình **Role-Based Access Control (RBAC)**, nghĩa là quyền hạn không được gán trực tiếp cho từng người mà được gán qua các **Nhóm Quyền**.

### Quy trình phân quyền:
1.  **Định nghĩa Quyền**: Các hành động cụ thể trên hệ thống (Ví dụ: `Xem hồ sơ`, `Thêm hồ sơ`, `Xóa hồ sơ`).
2.  **Tạo Nhóm Quyền**: Gom các quyền liên quan lại thành một nhóm (Ví dụ: Nhóm "Nhân viên tín dụng" sẽ có quyền Thêm/Sửa/Xem hồ sơ nhưng không có quyền Xóa).
3.  **Gán Người Dùng vào Nhóm**: Khi một người dùng được thêm vào nhóm, họ sẽ tự động có tất cả các quyền của nhóm đó.

> [!TIP]
> Một người dùng có thể thuộc nhiều Nhóm Quyền. Quyền hạn thực tế của họ sẽ là **tổng hợp** tất cả các quyền từ các nhóm đó.

---

## 3. Quản Lý Truy Cập (Dành cho Admin)

Trong giao diện **Quản lý Truy cập & Hệ thống**, Quản trị viên cần lưu ý:

*   **Trạng thái Hoạt động**: Một tài khoản nếu bị khóa (`Locked`) sẽ không thể đăng nhập dù có đủ quyền hạn.
*   **Quyền ROOT**: Chỉ tài khoản ROOT mới có thể cấp hoặc tước quyền ROOT của người khác.
*   **Nhật ký hệ thống (Audit Log)**: Mọi hành động nhạy cảm (Đăng nhập, Thay đổi quyền, Xóa dữ liệu) đều được ghi lại để phục vụ công tác hậu kiểm.

---

## 4. Nguyên Tắc Bảo Mật Cần Tuân Thủ

1.  **Nguyên tắc Quyền tối thiểu**: Chỉ cấp những quyền vừa đủ để người dùng hoàn thành công việc.
2.  **Không chia sẻ tài khoản**: Mỗi cá nhân phải sử dụng tài khoản riêng để đảm bảo tính minh bạch trongAudit Log.
3.  **Kiểm tra định kỳ**: Quản trị viên nên rà soát danh sách quyền của các nhóm định kỳ mỗi quý.

---
*Tài liệu này thuộc sở hữu của hệ thống Quản lý Soạn thảo Hợp đồng - Vietbank.*

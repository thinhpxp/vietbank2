# Kiến trúc Hệ thống Phân quyền (Permission Architecture)

Tài liệu này giải thích cơ chế phân quyền, kiểm soát truy cập và cách các tầng bảo vệ hoạt động cùng nhau trong ứng dụng VietBank Contract Automation.

## 1. Tổng quan: Ba Trụ cột của Danh tính (The Three Pillars of Identity)

Hệ thống quản lý người dùng dựa trên 3 lớp kiểm tra, hoạt động như các cánh cổng kế tiếp nhau:

### Lớp 1: Trạng thái Tài khoản (The Gatekeeper)
*   **Tham số:** `is_active` (Trên giao diện: Checkbox **"Hoạt động"**)
*   **Ý nghĩa:** Đây là công tắc tổng. Nếu tắt (unchecked), user không thể đăng nhập vào bất kỳ đâu, kể cả trang chủ hay admin.
*   **Khi nào dùng:** Kích hoạt tài khoản mới hoặc vô hiệu hóa nhân viên đã nghỉ việc.

### Lớp 2: Vai trò Hệ thống (The Master Keys)
Đây là các cờ đặc biệt dành cho đội ngũ kỹ thuật hoặc quản trị cấp cao.
*   **Quyền Admin (`is_staff`):**
    *   Cho phép truy cập vào trang quản trị (`/admin`).
    *   *Lưu ý cũ:* Trước đây, bắt buộc phải tích ô này thì User mới vào được Admin. **Hiện tại không còn bắt buộc** (xem phần Smart Access bên dưới).
*   **Quyền Root (`is_superuser`):**
    *   Quyền lực tuyệt đối. Bỏ qua mọi kiểm tra quyền hạn.
    *   Có thể xóa nát hệ thống, chỉnh sửa mọi thứ.
    *   **Cảnh báo:** Chỉ dành cho Dev hoặc CIO/CTO.

### Lớp 3: Vai trò Chức năng (RBAC - The Smart Keys)
Đây là lớp phân quyền linh hoạt dùng cho vận hành nghiệp vụ hàng ngày.
*   **Nhóm (Groups):** Tập hợp các quyền (ví dụ: Nhóm "Pháp chế", Nhóm "Soạn thảo").
*   **Quyền (Permissions):** Các hành động cụ thể (ví dụ: `view_user` - Xem danh sách user, `change_field` - Sửa trường thông tin).

---

## 2. Cơ chế "Smart Implicit Access" (Truy cập Thông minh)

Trước đây, có một sự "chồng chéo" khiến người quản trị bối rối: Muốn user vào sửa Lĩnh vực (Field), Root phải vừa gán User vào nhóm "Pháp chế", vừa phải nhớ tích vào "Quyền Admin".

**Hiện tại (Sau khi nâng cấp):** Hệ thống đã áp dụng cơ chế **Suy diễn Quyền (Implicit Authority)**.

### Nguyên lý hoạt động:
*"Nếu bạn được giao chìa khóa của két sắt (Quyền), bạn đương nhiên được đi qua cửa chính (Admin) để vào mở két."*

Hệ thống tự động kiểm tra:
1.  User có phải là **Staff/Root** không? -> Nếu có: **Vào**.
2.  *Nếu không:* User có sở hữu **bất kỳ** quyền quản trị nào không? (Ví dụ: `view_user`, `view_template`, `view_field`...)
    *   Nếu có -> Hệ thống tự động coi user này là **Admin** và mở cửa cho vào trang quản trị.
    *   User chỉ nhìn thấy và thao tác được đúng những gì họ được cấp quyền (Ví dụ: Chỉ thấy mục "Trường thông tin", không thấy "Người dùng").

## 3. Hướng dẫn Phân quyền (Best Practices)

Để tránh nhầm lẫn, hãy tuân theo quy tắc sau:

| Đối tượng | Cách cấu hình khuyên dùng | Giải thích |
| :--- | :--- | :--- |
| **End-User (NV K.Doanh)** | Chỉ tích **Hoạt động**. Gán vào nhóm nghiệp vụ (nếu cần). | Họ chỉ dùng Dashboard bên ngoài, không vào Admin. |
| **Quản trị viên Nghiệp vụ (NV Pháp chế, Admin con)** | Tích **Hoạt động**. Gán vào nhóm chức năng (VD: "Q.Lý Mẫu HĐ"). **KHÔNG** cần tích Admin/Root. | Hệ thống *Smart Access* sẽ tự cho họ vào Admin để sửa Mẫu HĐ. |
| **Đội IT / System Admin** | Tích **Hoạt động** + **Quyền Admin**. | Để họ có quyền truy cập kỹ thuật rộng hơn. |
| **Super Admin (ROOT)** | Tích **Hoạt động** + **Quyền Root**. | Dùng để cứu hộ hệ thống hoặc phân quyền cấp cao. |

## 4. Bảng Tra cứu nhanh UI

Trong màn hình "Chi tiết User" (`AdminAccessManagement`):

*   **Checkbox "Hoạt động":** `is_active` (Bắt buộc phải tích).
*   **Checkbox "Quyền Admin":** `is_staff` (**Đã ẩn trên UI** - Hệ thống tự động xử lý, User không cần quan tâm).
*   **Checkbox "Quyền Root":** `is_superuser` (Cực kỳ hạn chế dùng).
*   **Phần "Nhóm quyền" (Groups):** Nơi cấu hình chính cho các user nghiệp vụ (Manager, Tester, Content Creator...).

---
*Tài liệu này được cập nhật ngày 03/02/2026 sau bản nâng cấp Smart Access Control.*

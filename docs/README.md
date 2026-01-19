# Vietbank Contract App - Chỉ mục Tài liệu

## 📚 Tổng quan

Chào mừng đến với tài liệu hệ thống Vietbank Contract App. Tài liệu được chia thành hai phần chính:
- **Hướng dẫn người dùng** (User Guide): Dành cho người dùng cuối
- **Tài liệu kỹ thuật** (Developer Documentation): Dành cho lập trình viên

---

## 👥 Hướng dẫn Người dùng

### Bắt đầu
- **[Quản lý Tài khoản](./user-guide/account-management.md)**
  - Cập nhật thông tin cá nhân
  - Đổi mật khẩu
  - Xem quyền hạn
  - Đăng ký tài khoản mới

### Quản trị viên
- **[Hướng dẫn Admin Panel](./user-guide/admin-panel-guide.md)**
  - Quản lý người dùng
  - Quản lý nhóm và quyền hạn
  - Cấu hình trường thông tin
  - Xem nhật ký hệ thống

- **[Hướng dẫn Cấu hình Hệ thống](./user-guide/system-configuration-guide.md)** ⭐ *Mới*
  - Hiểu cơ chế Forms, Groups, Objects, Fields
  - Quy trình cấu hình hệ thống
  - Best practices cho quản trị viên
  - FAQ và xử lý sự cố

---

## 💻 Tài liệu Kỹ thuật (Developer)

### Kiến trúc Hệ thống
- **[Kiến trúc Frontend](./developer/architecture/frontend-structure.md)**
  - Cấu trúc dự án Vue 3
  - Kiến trúc component
  - Quản lý state (Vuex)
  - Routing & navigation
  - Mẫu tích hợp API

- **[API Backend](./developer/architecture/backend-api.md)**
  - Django REST Framework
  - Xác thực & ủy quyền
  - Tham chiếu API endpoints
  - Models & serializers
  - Hệ thống phân quyền

### UI Components & Design System
- **[Hướng dẫn Design System](./developer/ui-components/design-system.md)** ⭐ *Quan trọng*
  - Design tokens (màu sắc, khoảng cách, typography)
  - Hệ thống button & biến thể
  - Form controls
  - Layout components
  - Thực hành tốt nhất

- **[Hệ thống Icon SVG](./developer/ui-components/svg-icon-system.md)** ⭐ *Quan trọng*
  - Tham chiếu API component
  - 30+ icon có sẵn
  - Mẫu sử dụng
  - Thêm icon mới
  - Di chuyển từ emoji

- **[Tích hợp BaseModal](./developer/ui-components/basemodal-integration.md)**
  - Component modal có thể tái sử dụng
  - Props và slots
  - Ví dụ sử dụng
  - Best practices

- **[Xử lý Lỗi với ConfirmModal](./developer/ui-components/error-handling-guide.md)** ⭐ *Mới*
  - Hiển thị lỗi chi tiết với error code
  - Error handling utility và mixin
  - Best practices cho error handling
  - Migration từ alert() native

---

## 🚀 Bắt đầu Nhanh

### Cho Người dùng
1. Đọc [Quản lý Tài khoản](./user-guide/account-management.md) để biết cách sử dụng cơ bản
2. Nếu là Admin, xem [Hướng dẫn Admin Panel](./user-guide/admin-panel-guide.md)

### Cho Developer
1. Đọc [Kiến trúc Frontend](./developer/architecture/frontend-structure.md) để hiểu cấu trúc dự án
2. Xem [Hướng dẫn Design System](./developer/ui-components/design-system.md) trước khi code UI
3. Tham khảo [Hệ thống Icon SVG](./developer/ui-components/svg-icon-system.md) khi cần dùng icon
4. Đọc [API Backend](./developer/architecture/backend-api.md) để tích hợp API

---

## 📋 Cấu trúc Tài liệu

```
docs/
├── README.md (file này)
├── user-guide/
│   ├── account-management.md
│   └── admin-panel-guide.md
└── developer/
    ├── architecture/
    │   ├── frontend-structure.md
    │   └── backend-api.md
    └── ui-components/
        ├── design-system.md
        └── svg-icon-system.md
```

---

## 🔄 Lịch sử Cập nhật

### Version 1.0 (18/01/2026)
- ✅ Tài liệu quản lý tài khoản
- ✅ Hướng dẫn Admin Panel
- ✅ Design System Guidelines
- ✅ SVG Icon System Documentation
- ✅ Frontend Architecture
- ✅ Backend API Documentation

### Version 1.1 (19/01/2026)
- ✅ Dịch toàn bộ tài liệu kỹ thuật sang tiếng Việt

---

## 🆘 Hỗ trợ

### Người dùng
- **Email**: support@vietbank.com
- **Hotline**: 1900-xxxx

### Developer
- **Technical Lead**: [Tên người phụ trách]
- **Email**: dev-team@vietbank.com
- **Internal Wiki**: [Link nếu có]

---

## 📌 Lưu ý Quan trọng

### Cho Người dùng
- Đọc kỹ phần **Bảo mật** trong tài liệu quản lý tài khoản
- Thay đổi mật khẩu định kỳ
- Không chia sẻ thông tin đăng nhập

### Cho Developer
- **Luôn tuân thủ Design System** khi phát triển UI mới
- **Sử dụng SVG Icon** thay vì emoji
- **Kiểm tra tài liệu API** trước khi tích hợp
- **Viết test** cho code mới
- **Cập nhật tài liệu** khi thêm tính năng

---

## 🎯 Thực hành Tốt nhất

### Phát triển UI
1. Sử dụng design tokens từ `tokens.scss`
2. Áp dụng `.btn-action` cho tất cả button
3. Dùng `<SvgIcon>` component cho icon
4. Tuân thủ hướng dẫn spacing và color

### Tích hợp API
1. Sử dụng Axios interceptors cho authentication
2. Xử lý lỗi đầy đủ (try-catch)
3. Hiển thị loading states
4. Validate input trước khi gửi API

### Chất lượng Code
1. Tuân theo Vue 3 Composition API best practices
2. Đặt tên component có ý nghĩa
3. Giữ component tập trung và tái sử dụng được
4. Ghi chú logic phức tạp

---

## 📖 Đọc thêm

- [Vue 3 Official Docs](https://vuejs.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Material Design Guidelines](https://material.io/design)

---

**Phiên bản tài liệu**: 1.1  
**Cập nhật lần cuối**: 19/01/2026  
**Người bảo trì**: Vietbank Development Team

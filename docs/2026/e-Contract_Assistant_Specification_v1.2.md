# Tài liệu Đặc tả Hệ thống e-Contract Assistant
# System Specification Document

---

**Phiên bản (Version):** 1.2  
**Ngày phát hành (Release Date):** Tháng 2/2026  
**Tác giả (Author):** Phan Xuân Phước Thịnh  
**Khách hàng (Client):** Ngân hàng TMCP Việt Nam Thương Tín - Chi nhánh Đăk Lăk (Vietbank Đăk Lăk)  
**Thời gian phát triển (Development Period):** Tháng 9/2025 - Tháng 2/2026  

---

## Mục lục (Table of Contents)

1. [Giới thiệu (Introduction)](#1-giới-thiệu-introduction)
2. [Tổng quan hệ thống (System Overview)](#2-tổng-quan-hệ-thống-system-overview)
3. [Công nghệ sử dụng (Technology Stack)](#3-công-nghệ-sử-dụng-technology-stack)
4. [Đặc tả chức năng (Functional Specification)](#4-đặc-tả-chức-năng-functional-specification)
5. [Kiến trúc hệ thống (System Architecture)](#5-kiến-trúc-hệ-thống-system-architecture)
6. [Cấu trúc Cơ sở dữ liệu (Database Schema)](#6-cấu-trúc-cơ-sở-dữ-liệu-database-schema)
7. [Tài liệu API (API Documentation)](#7-tài-liệu-api-api-documentation)
8. [Hướng dẫn thiết kế Template .docx (Template Design Guide)](#8-hướng-dẫn-thiết-kế-template-docx-template-design-guide)
9. [Hướng dẫn cài đặt & triển khai (Installation Guide)](#9-hướng-dẫn-cài-đặt--triển-khai-installation-guide)
10. [Phụ lục (Appendix)](#10-phụ-lục-appendix)

---

## 1. Giới thiệu (Introduction)

### 1.1. Mục đích tài liệu (Document Purpose)
Tài liệu này cung cấp đặc tả kỹ thuật đầy đủ về hệ thống **e-Contract Assistant** - một ứng dụng web hỗ trợ quy trình soạn thảo hợp đồng tín dụng tự động cho Ngân hàng Vietbank Chi nhánh Đăk Lăk.

### 1.2. Phạm vi (Scope)
Hệ thống e-Contract Assistant được thiết kế để:
- **Quản lý thông tin khách hàng và tài sản bảo đảm** một cách linh hoạt, có thể mở rộng
- **Tự động hóa việc soạn thảo văn bản/hợp đồng** từ các mẫu template định sẵn
- **Giảm thiểu lỗi nhập liệu** và tăng tốc quy trình xử lý hồ sơ vay

### 1.3. Đối tượng sử dụng (Target Users)
| Vai trò | Mô tả |
|---------|-------|
| **Chuyên viên (Staff)** | Nhập liệu hồ sơ, xuất văn bản |
| **Quản lý (Manager)** | Giám sát, phê duyệt hồ sơ, quản lý dữ liệu Master |
| **Quản trị viên (Admin)** | Quản lý người dùng, phân quyền, cấu hình hệ thống |

---

## 2. Tổng quan hệ thống (System Overview)

### 2.1. Mô tả chung (General Description)
e-Contract Assistant là ứng dụng web được xây dựng theo kiến trúc **Client-Server** với:
- **Frontend**: Single Page Application (SPA) sử dụng Vue.js
- **Backend**: RESTful API sử dụng Django REST Framework
- **Database**: PostgreSQL (Production) / SQLite (Development)

### 2.2. Sơ đồ tổng quan (High-Level Diagram)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           NGƯỜI DÙNG (Users)                            │
│                  Chuyên viên | Quản lý | Quản trị viên                  │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTP/HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Vue.js 3 SPA)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ Dashboard    │  │ Loan Profile │  │ Admin Panel  │                   │
│  │ View         │  │ Form         │  │ Management   │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ REST API (JSON)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                BACKEND (Django REST Framework)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ ViewSets     │  │ Serializers  │  │ Document     │                   │
│  │ (API Logic)  │  │ (Data Trans) │  │ Generator    │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ ORM
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL/SQLite)                         │
│         Hồ sơ vay | Khách hàng | Tài sản | Template | Audit Log         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Công nghệ sử dụng (Technology Stack)

### 3.1. Backend Technologies

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Python** | 3.10+ | Ngôn ngữ lập trình Backend |
| **Django** | 5.2.7 | Web Framework chính |
| **Django REST Framework** | 3.16.1 | Xây dựng RESTful API |
| **djangorestframework-simplejwt** | 5.5.1 | Xác thực JWT Token |
| **django-filter** | 25.2 | Lọc dữ liệu API |
| **django-cors-headers** | 4.9.0 | Xử lý CORS cho Frontend |
| **django-cleanup** | 9.0.0 | Tự động dọn dẹp file upload |

### 3.2. Document Generation Technologies

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Jinja2** | 3.1.6 | Template Engine |
| **docxtpl** | 0.20.2 | Render template Word (.docx) |
| **python-docx** | 1.2.0 | Xử lý file Word |
| **num2words** | 0.5.14 | Chuyển số thành chữ (Tiếng Việt) |
| **lxml** | 6.0.2 | Xử lý XML trong Word |

### 3.3. Database

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **SQLite** | Built-in | Dev/Testing Database |
| **PostgreSQL** | 14+ | Production Database |
| **psycopg2-binary** | 2.9.11 | PostgreSQL Driver |

### 3.4. Frontend Technologies

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Vue.js** | 3.2.13 | JavaScript Framework (SPA) |
| **Vue Router** | 4.6.3 | Client-side Routing |
| **Axios** | 1.13.2 | HTTP Client cho API calls |
| **date-fns** | 4.1.0 | Xử lý ngày tháng |
| **SASS** | 1.97.2 | CSS Preprocessor |
| **Vue CLI** | 5.0 | Build Tool |

---

## 4. Đặc tả chức năng (Functional Specification)

### 4.1. Chức năng chính: Quản lý Khách hàng & Tài sản (Customer & Asset Management)

#### 4.1.1. Mô tả
Hệ thống cho phép quản lý thông tin khách hàng (cá nhân/tổ chức) và các loại tài sản bảo đảm một cách linh hoạt thông qua kiến trúc **Universal Entity**.

#### 4.1.2. Tính năng chi tiết

| Tính năng | Mô tả |
|-----------|-------|
| **Tạo Khách hàng mới** | Nhập thông tin cá nhân: họ tên, CCCD, ngày sinh, địa chỉ, SĐT |
| **Gán vai trò (Role)** | Gán vai trò cho khách hàng: Bên thế chấp, Bên vay, Người nhận tiền... |
| **Quản lý Tài sản** | Thêm/sửa/xóa tài sản: Bất động sản, Xe cộ, Sổ tiết kiệm, Trái phiếu... |
| **Liên kết quan hệ** | Thiết lập quan hệ giữa các đối tượng: Chủ sở hữu, Người liên quan... |
| **Tái sử dụng dữ liệu** | Chọn khách hàng/tài sản đã có từ Master Data để liên kết vào hồ sơ mới |

#### 4.1.3. Các loại đối tượng hỗ trợ (Object Types)

| Mã loại | Tên hiển thị | Mô tả |
|---------|--------------|-------|
| `PERSON` | Cá nhân | Thông tin khách hàng cá nhân |
| `REALESTATE` | Bất động sản | Quyền sử dụng đất, nhà ở |
| `VEHICLE` | Phương tiện | Ô tô, xe máy |
| `SAVINGS` | Sổ tiết kiệm | Thẻ tiết kiệm, sổ tiền gửi |
| `BOND` | Trái phiếu | Trái phiếu, giấy tờ có giá |
| `HDTD_TL` | HĐTD Từng lần | Hợp đồng tín dụng từng lần |
| `HDTD_HM` | HĐTD Hạn mức | Hợp đồng tín dụng hạn mức |

---

### 4.2. Chức năng chính: Soạn thảo Văn bản tự động (Automatic Document Drafting)

#### 4.2.1. Mô tả
Hệ thống tự động điền thông tin từ hồ sơ vào các mẫu văn bản Word (.docx) và xuất file hoàn chỉnh.

#### 4.2.2. Quy trình hoạt động

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 1. Chọn hồ sơ│───>│ 2. Chọn mẫu  │───>│ 3. Hệ thống  │───>│ 4. Tải file  │
│    vay       │    │    template  │    │    render    │    │    .docx     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

#### 4.2.3. Tính năng Template Engine

| Tính năng | Cú pháp | Ví dụ |
|-----------|---------|-------|
| **Chèn biến** | `{{ tên_biến }}` | `{{ ho_ten }}` |
| **Vòng lặp** | `{% for x in list %}...{% endfor %}` | In danh sách tài sản |
| **Điều kiện** | `{% if biến %}...{% endif %}` | Hiển thị nếu có dữ liệu |
| **Định dạng tiền** | `{{ số | format_currency }}` | 1.000.000 |
| **Số thành chữ** | `{{ số | num2words }}` | Một triệu đồng |
| **Định dạng ngày** | `{{ ngày | dateformat }}` | 31/12/2025 |

---

### 4.3. Các chức năng hỗ trợ (Supporting Functions)

#### 4.3.1. Quản lý Hồ sơ vay (Loan Profile Management)

| Tính năng | Mô tả |
|-----------|-------|
| Tạo hồ sơ mới | Khởi tạo hồ sơ với trạng thái DRAFT |
| Lưu hồ sơ | Lưu thông tin và các đối tượng liên quan |
| Khóa hồ sơ | Chuyển trạng thái sang FINALIZED để ngăn chỉnh sửa |
| Mở khóa hồ sơ | Nhập mật khẩu để mở khóa và tiếp tục chỉnh sửa |
| Xóa hồ sơ | Xóa hồ sơ và các liên kết liên quan |

#### 4.3.2. Quản trị hệ thống (System Administration)

| Module | Chức năng |
|--------|-----------|
| **Quản lý User** | CRUD người dùng, reset password |
| **Quản lý Role/Group** | Phân quyền theo nhóm chức năng |
| **Audit Log** | Ghi nhận mọi thao tác: Login, Create, Update, Delete |
| **Master Data** | Quản lý Field, FieldGroup, ObjectType, Template |

---

## 5. Kiến trúc hệ thống (System Architecture)

### 5.1. Sơ đồ Kiến trúc tổng thể (Architecture Diagram)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                           │
├───────────────────────────────────────────────────────────────────────────┤
│  Views (Vue Components)                                                   │
│  ├── DashboardView.vue        - Trang tổng quan                          │
│  ├── LoanProfileForm.vue      - Form nhập liệu hồ sơ vay                 │
│  ├── Login.vue / Register.vue - Xác thực người dùng                      │
│  └── admin/                   - Các trang quản trị                       │
│       ├── MasterData.vue      - Quản lý dữ liệu Master                   │
│       ├── AdminUsers.vue      - Quản lý người dùng                       │
│       ├── AdminAuditLog.vue   - Xem nhật ký hệ thống                     │
│       └── ...                                                             │
├───────────────────────────────────────────────────────────────────────────┤
│  Components (Shared UI)                                                   │
│  ├── PersonForm.vue           - Form nhập thông tin khách hàng           │
│  ├── AssetForm.vue            - Form nhập thông tin tài sản              │
│  ├── RelationManager.vue      - Quản lý liên kết đối tượng               │
│  ├── ContractDownloader.vue   - Xuất văn bản                             │
│  ├── ObjectSelectModal.vue    - Chọn đối tượng từ Master Data            │
│  └── ...                                                                  │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API (JSON over HTTP)
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                              BUSINESS LAYER                               │
├───────────────────────────────────────────────────────────────────────────┤
│  ViewSets (Django REST Framework)                                         │
│  ├── LoanProfileViewSet       - CRUD hồ sơ vay + xuất văn bản            │
│  ├── MasterObjectViewSet      - CRUD đối tượng Master                    │
│  ├── FieldViewSet             - CRUD trường dữ liệu                      │
│  ├── UserViewSet              - Quản lý người dùng                       │
│  ├── AuditLogViewSet          - Truy vấn nhật ký (Read-only)             │
│  └── ...                                                                  │
├───────────────────────────────────────────────────────────────────────────┤
│  Services                                                                 │
│  ├── Document Generator       - Render template Word                     │
│  ├── Jinja2 Filters           - format_currency, num2words, dateformat   │
│  └── Audit Logger             - Ghi log thao tác                         │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Django ORM
                                    ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                   │
├───────────────────────────────────────────────────────────────────────────┤
│  Models (Database Tables)                                                 │
│  ├── LoanProfile              - Hồ sơ vay                                │
│  ├── MasterObject             - Đối tượng động (Khách hàng, Tài sản)     │
│  ├── MasterObjectType         - Loại đối tượng                           │
│  ├── Field / FieldGroup       - Định nghĩa trường dữ liệu                │
│  ├── FieldValue               - Giá trị thực của trường                  │
│  ├── DocumentTemplate         - Mẫu văn bản                              │
│  ├── AuditLog                 - Nhật ký hệ thống                         │
│  └── ...                                                                  │
└───────────────────────────────────────────────────────────────────────────┘
```

### 5.2. Chi tiết Component Frontend

| Component | File | Nhiệm vụ |
|-----------|------|----------|
| **DashboardView** | `views/DashboardView.vue` | Hiển thị danh sách hồ sơ vay, bộ lọc, thao tác nhanh |
| **LoanProfileForm** | `views/LoanProfileForm.vue` | Form chính nhập liệu hồ sơ, quản lý khách hàng/tài sản |
| **Login** | `views/Login.vue` | Xác thực người dùng bằng JWT |
| **Register** | `views/Register.vue` | Đăng ký tài khoản mới |
| **ProfileView** | `views/ProfileView.vue` | Xem/sửa thông tin cá nhân |
| **PersonForm** | `components/PersonForm.vue` | Form nhập thông tin khách hàng |
| **AssetForm** | `components/AssetForm.vue` | Form nhập thông tin tài sản |
| **DynamicForm** | `components/DynamicForm.vue` | Render form động theo cấu hình |
| **RelationManager** | `components/RelationManager.vue` | Quản lý quan hệ giữa các đối tượng |
| **ContractDownloader** | `components/ContractDownloader.vue` | Chọn template và xuất văn bản |
| **ObjectSelectModal** | `components/ObjectSelectModal.vue` | Modal chọn đối tượng từ Master Data |
| **MasterCreateModal** | `components/MasterCreateModal.vue` | Modal tạo đối tượng Master mới |
| **ObjectDetailModal** | `components/ObjectDetailModal.vue` | Xem chi tiết đối tượng |
| **BaseModal** | `components/BaseModal.vue` | Component modal tái sử dụng |
| **ConfirmModal** | `components/ConfirmModal.vue` | Modal xác nhận hành động |
| **AppToast** | `components/AppToast.vue` | Hiển thị thông báo toast |

### 5.3. Chi tiết Component Admin

| Component | File | Nhiệm vụ |
|-----------|------|----------|
| **AdminLayout** | `admin/AdminLayout.vue` | Layout chung cho trang Admin |
| **MasterData** | `admin/MasterData.vue` | Quản lý Field, Group, ObjectType, Template, Role |
| **AdminUsers** | `admin/AdminUsers.vue` | CRUD người dùng |
| **AdminRoles** | `admin/AdminRoles.vue` | Quản lý vai trò |
| **AdminFields** | `admin/AdminFields.vue` | Quản lý trường dữ liệu |
| **AdminGroups** | `admin/AdminGroups.vue` | Quản lý nhóm trường |
| **AdminObjectTypes** | `admin/AdminObjectTypes.vue` | Quản lý loại đối tượng |
| **AdminTemplates** | `admin/AdminTemplates.vue` | Upload/quản lý mẫu văn bản |
| **AdminForms** | `admin/AdminForms.vue` | Cấu hình Form View |
| **AdminAuditLog** | `admin/AdminAuditLog.vue` | Xem nhật ký hệ thống |
| **AdminAccessManagement** | `admin/AdminAccessManagement.vue` | Phân quyền chi tiết |

### 5.4. Chi tiết Module Backend

| Module | File | Nhiệm vụ |
|--------|------|----------|
| **models.py** | `document_automation/models.py` | Định nghĩa 13 bảng cơ sở dữ liệu |
| **views.py** | `document_automation/views.py` | 14 ViewSets xử lý logic API |
| **serializers.py** | `document_automation/serializers.py` | Chuyển đổi Model ↔ JSON |
| **urls.py** | `document_automation/urls.py` | Định nghĩa routing API |
| **permissions.py** | `document_automation/permissions.py` | Custom permission classes |
| **filters.py** | `document_automation/filters.py` | Bộ lọc Django Filter |

---

## 6. Cấu trúc Cơ sở dữ liệu (Database Schema)

### 6.1. Danh sách bảng (Table List)

| STT | Tên bảng | Mô tả | Số trường |
|-----|----------|-------|-----------|
| 1 | `FormView` | Cấu hình Form hiển thị | 3 |
| 2 | `FieldGroup` | Nhóm các trường dữ liệu | 9 |
| 3 | `Field` | Định nghĩa trường dữ liệu | 14 |
| 4 | `Role` | Vai trò của khách hàng | 5 |
| 5 | `DocumentTemplate` | Mẫu văn bản Word | 5 |
| 6 | `LoanProfile` | Hồ sơ vay | 7 |
| 7 | `MasterObjectType` | Loại đối tượng động | 11 |
| 8 | `MasterObject` | Container đối tượng chung | 5 |
| 9 | `LoanProfileObjectLink` | Liên kết hồ sơ - đối tượng | 3 |
| 10 | `FieldValue` | Giá trị thực của trường | 4 |
| 11 | `UserProfile` | Thông tin mở rộng User | 6 |
| 12 | `AuditLog` | Nhật ký thao tác | 6 |
| 13 | `MasterObjectRelation` | Quan hệ giữa các đối tượng | 5 |

### 6.2. Chi tiết từng bảng (Table Details)

#### 6.2.1. Bảng `LoanProfile` (Hồ sơ vay)

| Trường | Kiểu dữ liệu | Nullable | Mô tả |
|--------|--------------|----------|-------|
| `id` | INTEGER (PK) | No | Khóa chính tự tăng |
| `name` | VARCHAR(255) | No | Tên hồ sơ |
| `status` | VARCHAR(20) | No | Trạng thái: DRAFT / FINALIZED |
| `form_view_id` | INTEGER (FK) | Yes | Liên kết đến FormView |
| `created_by_user_id` | INTEGER (FK) | Yes | Người tạo |
| `lock_password` | VARCHAR(100) | Yes | Mật khẩu khóa hồ sơ |
| `created_at` | DATETIME | No | Thời gian tạo |
| `updated_at` | DATETIME | No | Thời gian cập nhật |

#### 6.2.2. Bảng `MasterObject` (Đối tượng động)

| Trường | Kiểu dữ liệu | Nullable | Mô tả |
|--------|--------------|----------|-------|
| `id` | INTEGER (PK) | No | Khóa chính tự tăng |
| `object_type` | VARCHAR(20) | No | Mã loại (PERSON, REALESTATE...) |
| `deleted_at` | DATETIME | Yes | Soft delete timestamp |
| `last_updated_by_id` | INTEGER (FK) | Yes | Người cập nhật cuối |
| `created_at` | DATETIME | No | Thời gian tạo |
| `updated_at` | DATETIME | No | Thời gian cập nhật |

#### 6.2.3. Bảng `FieldValue` (Giá trị trường)

| Trường | Kiểu dữ liệu | Nullable | Mô tả |
|--------|--------------|----------|-------|
| `id` | INTEGER (PK) | No | Khóa chính tự tăng |
| `loan_profile_id` | INTEGER (FK) | Yes | Liên kết hồ sơ (cho profile-level data) |
| `master_object_id` | INTEGER (FK) | Yes | Liên kết đối tượng (cho object-level data) |
| `field_id` | INTEGER (FK) | No | Liên kết Field định nghĩa |
| `value` | TEXT | No | Giá trị thực tế |

#### 6.2.4. Bảng `Field` (Định nghĩa trường)

| Trường | Kiểu dữ liệu | Nullable | Mô tả |
|--------|--------------|----------|-------|
| `id` | INTEGER (PK) | No | Khóa chính |
| `label` | VARCHAR(255) | No | Nhãn hiển thị |
| `placeholder_key` | VARCHAR(100) | No | Key dùng trong template (unique) |
| `data_type` | VARCHAR(50) | No | TEXT, NUMBER, DATE, TEXTAREA, CHECKBOX |
| `group_id` | INTEGER (FK) | Yes | Nhóm trường |
| `order` | INTEGER | No | Thứ tự hiển thị |
| `width_cols` | INTEGER | No | Độ rộng (1-12 cols) |
| `is_active` | BOOLEAN | No | Trạng thái kích hoạt |
| `is_protected` | BOOLEAN | No | Không cho phép xóa |
| `use_digit_grouping` | BOOLEAN | No | Phân tách hàng nghìn |
| `show_amount_in_words` | BOOLEAN | No | Hiển thị số thành chữ |
| `default_value` | TEXT | Yes | Giá trị mặc định |
| `css_class` | VARCHAR(255) | Yes | CSS class tùy chỉnh |
| `note` | TEXT | Yes | Ghi chú |

#### 6.2.5. Bảng `AuditLog` (Nhật ký)

| Trường | Kiểu dữ liệu | Nullable | Mô tả |
|--------|--------------|----------|-------|
| `id` | INTEGER (PK) | No | Khóa chính |
| `user_id` | INTEGER (FK) | Yes | Người thực hiện |
| `action` | VARCHAR(20) | No | LOGIN, LOGOUT, CREATE, UPDATE, DELETE |
| `target_model` | VARCHAR(100) | No | Model bị tác động |
| `target_id` | VARCHAR(50) | Yes | ID đối tượng |
| `details` | TEXT | Yes | Chi tiết thay đổi |
| `timestamp` | DATETIME | No | Thời gian (indexed) |

### 6.3. Sơ đồ quan hệ (Entity Relationship Diagram)

```
┌────────────────┐       ┌─────────────────────┐       ┌────────────────┐
│   FormView     │       │    FieldGroup       │       │   ObjectType   │
├────────────────┤       ├─────────────────────┤       ├────────────────┤
│ id (PK)        │◄──────│ allowed_forms (M2M) │       │ id (PK)        │
│ name           │       │ id (PK)             │◄──────│ code           │
│ slug           │       │ name                │       │ name           │
│ note           │       │ entity_type         │       │ identity_field │
└────────────────┘       │ layout_position     │       └───────┬────────┘
                         │ order               │               │
                         └─────────┬───────────┘               │
                                   │                           │
                                   │ 1:N                       │
                                   ▼                           │
                         ┌─────────────────────┐               │
                         │      Field          │               │
                         ├─────────────────────┤               │
                         │ id (PK)             │               │
                         │ label               │               │
                         │ placeholder_key (U) │               │
                         │ data_type           │               │
                         │ group_id (FK)       │               │
                         └─────────┬───────────┘               │
                                   │                           │
                                   │ 1:N                       │
                                   ▼                           │
┌────────────────┐       ┌─────────────────────┐       ┌───────┴────────┐
│  LoanProfile   │       │    FieldValue       │       │  MasterObject  │
├────────────────┤       ├─────────────────────┤       ├────────────────┤
│ id (PK)        │◄──────│ loan_profile_id(FK) │       │ id (PK)        │
│ name           │       │ master_object_id(FK)│──────►│ object_type    │
│ status         │       │ field_id (FK)       │       │ deleted_at     │
│ created_by (FK)│       │ value               │       └───────┬────────┘
└───────┬────────┘       └─────────────────────┘               │
        │                                                       │
        │ M:N via LoanProfileObjectLink                        │
        │                                                       │
        └─────────────────┐                   ┌─────────────────┘
                          ▼                   ▼
                ┌─────────────────────────────────────┐
                │      LoanProfileObjectLink          │
                ├─────────────────────────────────────┤
                │ id (PK)                             │
                │ loan_profile_id (FK)                │
                │ master_object_id (FK)               │
                │ roles (JSON)                        │
                └─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                  MasterObjectRelation                          │
├────────────────────────────────────────────────────────────────┤
│ source_object_id (FK) ──► MasterObject                         │
│ target_object_id (FK) ──► MasterObject                         │
│ relation_type (VD: OWNER)                                      │
└────────────────────────────────────────────────────────────────┘
```

---

## 7. Tài liệu API (API Documentation)

### 7.1. Base URL
```
Development: http://localhost:8000/api/
Production:  https://[domain]/api/
```

### 7.2. Authentication
Hệ thống sử dụng **JWT (JSON Web Token)** cho xác thực:

```http
POST /api/token/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 7.3. Danh sách Endpoints

| Endpoint | Method | Mô tả | Permission |
|----------|--------|-------|------------|
| `/api/loan-profiles/` | GET, POST | Danh sách/Tạo hồ sơ vay | Authenticated |
| `/api/loan-profiles/{id}/` | GET, PUT, DELETE | Chi tiết/Sửa/Xóa hồ sơ | Authenticated |
| `/api/loan-profiles/{id}/generate_document/` | POST | Xuất văn bản | Authenticated |
| `/api/master-objects/` | GET, POST | Danh sách/Tạo đối tượng Master | Admin/Manager |
| `/api/master-objects/{id}/` | GET, PUT, DELETE | Chi tiết/Sửa/Xóa đối tượng | Admin/Manager |
| `/api/object-types/` | GET, POST | Danh sách loại đối tượng | Admin/Manager |
| `/api/fields/` | GET, POST | Danh sách trường dữ liệu | Admin/Manager |
| `/api/fields/active_fields_grouped/` | GET | Trường theo nhóm (cho form) | Authenticated |
| `/api/groups/` | GET, POST | Danh sách nhóm trường | Admin/Manager |
| `/api/document-templates/` | GET, POST | Danh sách mẫu văn bản | Admin/Manager |
| `/api/users/` | GET, POST | Danh sách người dùng | Admin |
| `/api/users/{id}/reset_password/` | POST | Reset mật khẩu | Admin |
| `/api/audit-logs/` | GET | Xem nhật ký (phân trang 15/page) | Admin/Manager |
| `/api/roles/` | GET, POST | Danh sách vai trò | Admin/Manager |
| `/api/me/` | GET, PUT | Thông tin cá nhân | Authenticated |
| `/api/change-password/` | POST | Đổi mật khẩu | Authenticated |
| `/api/register/` | POST | Đăng ký tài khoản | Public |

### 7.4. Chi tiết API quan trọng

#### 7.4.1. Tạo Hồ sơ vay

```http
POST /api/loan-profiles/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Hồ sơ vay - Nguyễn Văn A",
  "form_view": 1,
  "objects_data": [
    {
      "object_type": "PERSON",
      "roles": ["Bên thế chấp", "Bên vay"],
      "fields": {
        "ho_ten": "Nguyễn Văn A",
        "cccd": "012345678901",
        "ngay_sinh": "1990-01-15"
      }
    }
  ],
  "profile_fields": {
    "so_tien_vay": "500000000",
    "muc_dich_vay": "Mua nhà ở"
  }
}
```

#### 7.4.2. Xuất văn bản

```http
POST /api/loan-profiles/{id}/generate_document/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "template_id": 1
}

Response: Binary file (.docx)
```

---

## 8. Hướng dẫn thiết kế Template .docx (Template Design Guide)

### 8.1. Cú pháp Placeholder cơ bản

Sử dụng cú pháp Jinja2 trong file Word (.docx):

| Loại | Cú pháp | Ví dụ |
|------|---------|-------|
| **Biến đơn** | `{{ tên_biến }}` | `{{ ho_ten }}` |
| **Vòng lặp** | `{% for x in list %}...{% endfor %}` | Xem bên dưới |
| **Điều kiện** | `{% if biến %}...{% endif %}` | Xem bên dưới |

### 8.2. Danh sách Placeholder theo nhóm

#### Nhóm: Thông tin Khách hàng
| Placeholder | Mô tả |
|-------------|-------|
| `{{ ho_ten }}` | Họ và tên |
| `{{ cccd }}` | Số CCCD/CMND |
| `{{ ngay_cap_cccd }}` | Ngày cấp CCCD |
| `{{ noi_cap_cccd }}` | Nơi cấp CCCD |
| `{{ nam_sinh }}` | Năm sinh |
| `{{ dia_chi_thuong_tru }}` | Địa chỉ thường trú |
| `{{ dien_thoai }}` | Số điện thoại |

#### Nhóm: Tài sản - Bất động sản
| Placeholder | Mô tả |
|-------------|-------|
| `{{ dia_chi_thua_dat }}` | Địa chỉ thửa đất |
| `{{ thua_dat_so }}` | Số thửa đất |
| `{{ to_ban_do }}` | Số tờ bản đồ |
| `{{ dien_tich_thua_dat }}` | Diện tích |
| `{{ chung_nhan_qsdd }}` | Số GCN QSDĐ |
| `{{ ngay_cap_gcn }}` | Ngày cấp GCN |

### 8.3. Vòng lặp và Điều kiện

#### In danh sách khách hàng theo vai trò:
```jinja2
{% for p in ben_the_chap_list %}
Ông/Bà: {{ p.ho_ten }}, CCCD: {{ p.cccd }}
{% endfor %}
```

#### Hiển thị có điều kiện:
```jinja2
{% if hdtd_tl %}
HỢP ĐỒNG TÍN DỤNG TỪNG LẦN:
- Số hợp đồng: {{ hdtd_tl }}
- Số tiền vay: {{ hdtd_tl_so_tien_vay | format_currency }} VNĐ
{% endif %}

{% if hdtd_hm %}
HỢP ĐỒNG TÍN DỤNG HẠN MỨC:
- Số hợp đồng: {{ hdtd_hm }}
- Hạn mức: {{ hdtd_hm_so_tien_vay | format_currency }} VNĐ
{% endif %}
```

### 8.4. Bộ lọc định dạng (Filters)

| Filter | Cú pháp | Kết quả |
|--------|---------|---------|
| **Tiền tệ** | `{{ so_tien | format_currency }}` | 1.000.000 |
| **Số thành chữ** | `{{ so_tien | num2words }}` | Một triệu |
| **Ngày tháng** | `{{ ngay | dateformat }}` | 31/12/2025 |
| **Số La Mã** | `{{ stt | to_roman }}` | i, ii, iii |

---

## 9. Hướng dẫn cài đặt & triển khai (Installation Guide)

### 9.1. Yêu cầu hệ thống (System Requirements)

| Thành phần | Yêu cầu tối thiểu |
|------------|-------------------|
| **OS** | Windows 10+ / Ubuntu 20.04+ |
| **Python** | 3.10 hoặc cao hơn |
| **Node.js** | 18.x hoặc cao hơn |
| **RAM** | 4GB (khuyến nghị 8GB) |
| **Disk** | 1GB trống |
| **Database** | PostgreSQL 14+ (Production) |

### 9.2. Cài đặt Development

#### Bước 1: Clone source code
```bash
git clone <repository-url>
cd Webapp_vietbank
```

#### Bước 2: Cài đặt Backend
```bash
cd ContractDraftingWebapp
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Bước 3: Cài đặt Frontend
```bash
cd frontend
npm install
npm run serve
```

#### Bước 4: Truy cập
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin/

### 9.3. Cấu hình Production

#### Biến môi trường (Environment Variables)
```bash
DEBUG=False
SECRET_KEY=<random-secret-key>
DATABASE_URL=postgres://user:password@host:5432/dbname
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

#### Build Frontend
```bash
cd frontend
npm run build
# Copy thư mục dist/ lên web server
```

---

## 10. Phụ lục (Appendix)

### 10.1. Danh sách File quan trọng

| Đường dẫn | Mô tả |
|-----------|-------|
| `ContractDraftingWebapp/document_automation/models.py` | Định nghĩa Database |
| `ContractDraftingWebapp/document_automation/views.py` | Logic API |
| `ContractDraftingWebapp/document_automation/serializers.py` | Data transformers |
| `frontend/src/views/LoanProfileForm.vue` | Form nhập liệu chính |
| `frontend/src/components/ContractDownloader.vue` | Xuất văn bản |
| `docs/admin-guide/template-config.md` | Hướng dẫn cấu hình Template |

### 10.2. Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js 3 Documentation](https://vuejs.org/)
- [docxtpl Documentation](https://docxtpl.readthedocs.io/)
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/templates/)

### 10.3. Lịch sử phiên bản (Version History)

| Phiên bản | Ngày | Thay đổi chính |
|-----------|------|----------------|
| 1.0 | 12/2025 | Phiên bản đầu tiên |
| 1.1 | 01/2026 | Thêm Audit Log, cải thiện UI |
| 1.2 | 02/2026 | Tối ưu phân trang, thêm Master Data soft-delete |

---

**© 2026 - Phan Xuân Phước Thịnh**  
**Bản quyền thuộc về Ngân hàng Vietbank Chi nhánh Đăk Lăk**

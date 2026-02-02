# Hướng dẫn Quản trị: Chiến lược Bố cục Form (Master Object Types & Groups)

Tài liệu này hướng dẫn cách quản trị viên có thể tùy chỉnh toàn bộ giao diện hồ sơ vay mà không cần can thiệp vào mã nguồn.

## 1. Tổng quan mô hình "Hướng đối tượng" (Object-Driven)

Kể từ phiên bản mới nhất, hệ thống đã chuyển sang mô hình bố cục **100% dựa trên Loại đối tượng (Master Object Types)**. Điều này có nghĩa là:
- Mọi thành phần trên form (từ thông tin hồ sơ cốt lõi cho đến các danh sách tài sản, người liên quan) đều được coi là một **"Khối thông tin" (Object Section)**.
- Bố cục (Vị trí trái/phải, thứ tự trên/dưới) được thiết lập tập trung tại menu cấu hình **Loại Đối tượng**.

## 2. Phân biệt Master Object Type và Field Group

Quản trị viên cần nắm vững mối quan hệ giữa "Cái hộp" và "Nội dung" bên trong:

| Thành phần | Vai trò trong bố cục | Menu cấu hình |
| :--- | :--- | :--- |
| **Master Object Type** | Là **"Cái hộp" (Container)** lớn. Quyết định vị trí, màu sắc (nếu có) và thứ tự của cả một khối thông tin trên form. | Admin > Loại Đối tượng |
| **Field Group** | Là **"Cách nhóm"** các trường bên trong cái hộp đó. Giúp tổ chức các trường dữ liệu theo trình tự logic. | Admin > Nhóm thông tin |

## 3. Quản lý Bố cục (Layout Management)

Để thay đổi giao diện form, Quản trị viên thực hiện tại menu **Admin > Quản lý Loại Đối tượng**:

### A. Vị trí hiển thị (Layout Position)
- **Cột Trái (LEFT)**: Khối thông tin sẽ xuất hiện ở phía bên trái màn hình.
- **Cột Phải (RIGHT)**: Khối thông tin sẽ xuất hiện ở phía bên phải màn hình.

### B. Thứ tự hiển thị (Order)
- Hệ thống sắp xếp các khối từ trên xuống dưới dựa trên số **Thứ tự (Order)**. Số nhỏ hơn sẽ hiển thị cao hơn (ưu tiên trước).
- *Mẹo*: Bạn nên đặt Thứ tự theo các khoảng cách như 10, 20, 30... để dễ dàng chèn các khối mới vào giữa nếu phát sinh sau này.

### C. Chế độ hiển thị Form (Display Mode)
- **DEDICATED_SECTION**: Dùng cho các khối thông tin cố định hoặc duy nhất (như Thông tin hồ sơ `CONTRACT_HDTC`). Hệ thống sẽ tự động ẩn các nút "Thêm mới" hoặc "Xóa" để tránh nhầm lẫn.
- **ASSET_LIST / PERSON_LIST**: Dùng cho các danh sách cho phép người dùng thêm nhiều bản ghi (ví dụ: Danh sách tài sản, Danh sách người liên quan).

## 4. Quy trình tạo mới một phần thông tin

Khi quản trị viên muốn bổ sung một phần thông tin hoàn toàn mới (ví dụ: "Thông tin Bảo lãnh"):

1.  **Bước 1**: Tạo một **Master Object Type** mới (Mã: `BAO_LANH`, Tên: `Thông tin Bảo lãnh`). Thiết lập Vị trí và Thứ tự.
2.  **Bước 2**: Tạo một hoặc nhiều **Nhóm thông tin (Groups)** và gán chúng vào Loại đối tượng `Thông tin Bảo lãnh` vừa tạo.
3.  **Bước 3**: Tạo các **Trường dữ liệu (Fields)** và gán vào các Nhóm tương ứng.

## 5. Lưu ý quan trọng
- **Thông tin hồ sơ gốc**: Khối thông tin hồ sơ (mã `CONTRACT_HDTC`) hiện tại cũng là một Loại đối tượng. Bạn có thể di chuyển nó sang cột Phải hoặc đưa xuống cuối cùng nếu muốn bằng cách chỉnh sửa **Thứ tự** và **Vị trí** của chính nó.
- **Ẩn khối trống**: Nếu một Loại đối tượng được tạo nhưng không có bất kỳ Trường dữ liệu nào được gán vào (hoặc không có filed nào được phép hiển thị ở form hiện tại), khối đó sẽ tự động không hiển thị để tiết kiệm diện tích.

---
*Tài liệu hướng dẫn dành cho Quản trị viên hệ thống.*

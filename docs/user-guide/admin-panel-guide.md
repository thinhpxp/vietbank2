# Hướng dẫn sử dụng Admin Panel

## Giới thiệu

Admin Panel là khu vực quản trị dành cho người quản lý hệ thống Vietbank Contract App. Tại đây, bạn có thể quản lý người dùng, phân quyền, cấu hình nhóm thông tin, và theo dõi hoạt động của hệ thống.

## Truy cập Admin Panel

### Yêu cầu
- Tài khoản phải có quyền **Admin** hoặc **Superuser**
- Đã đăng nhập vào hệ thống

### Cách truy cập
1. Đăng nhập vào hệ thống
2. Nhấp vào **"⚙️ Admin Panel"** trên thanh điều hướng (navbar)
3. Bạn sẽ được chuyển đến trang quản trị

> **Lưu ý**: Nếu không thấy menu "Admin Panel", tài khoản của bạn chưa được cấp quyền quản trị.

## Các chức năng chính

### 1. Quản lý Người dùng (Users)

#### Xem danh sách người dùng
- Truy cập: **Admin Panel** → **Quản lý Truy cập** → Tab **"Người dùng"**
- Danh sách hiển thị: Username, Email, Họ tên, Trạng thái

#### Tìm kiếm người dùng
- Sử dụng ô **"Tìm kiếm user..."** ở đầu danh sách
- Nhập username hoặc email để lọc

#### Thêm người dùng mới
1. Nhấp nút **"➕ Thêm"** ở góc phải trên
2. Điền thông tin:
   - **Username** (bắt buộc, duy nhất)
   - **Email** (bắt buộc)
   - **Mật khẩu** (bắt buộc, tối thiểu 8 ký tự)
   - **Họ tên**
   - **Số điện thoại**
   - **Nơi làm việc**
   - **Phòng ban**
3. Chọn **Nhóm** và **Quyền hạn** (nếu cần)
4. Nhấp **"Lưu thay đổi"**

> **Mẹo**: Người dùng mới sẽ tự động được thêm vào nhóm **"soạn thảo"**

#### Chỉnh sửa thông tin người dùng
1. Nhấp vào tên người dùng trong danh sách
2. Cập nhật thông tin cần thiết
3. Chọn/bỏ chọn **Nhóm** và **Quyền hạn**
4. Nhấp **"Lưu thay đổi"**

#### Reset mật khẩu
1. Chọn người dùng cần reset
2. Nhấp nút **"🔄 Reset mật khẩu"**
3. Xác nhận hành động
4. Mật khẩu mới sẽ được gửi qua email (hoặc hiển thị trên màn hình)

#### Xóa tài khoản
1. Chọn người dùng cần xóa
2. Nhấp nút **"🗑️ Xóa tài khoản"**
3. Xác nhận hành động trong hộp thoại

> **Cảnh báo**: 
> - Không thể xóa tài khoản **Superuser** (có biểu tượng 🛡️)
> - Hành động xóa không thể hoàn tác

### 2. Quản lý Nhóm & Quyền (Groups & Permissions)

#### Xem danh sách nhóm
- Truy cập: **Admin Panel** → **Quản lý Truy cập** → Tab **"Nhóm & Quyền"**

#### Tạo nhóm mới
1. Nhấp nút **"➕ Tạo Nhóm"**
2. Nhập **Tên nhóm** (ví dụ: "Kế toán", "Pháp chế")
3. Chọn **Quyền hạn** cho nhóm
4. Nhấp **"Lưu Nhóm"**

#### Chỉnh sửa nhóm
1. Nhấp vào tên nhóm trong danh sách
2. Cập nhật tên hoặc quyền hạn
3. Nhấp **"Lưu Nhóm"**

#### Xóa nhóm
1. Chọn nhóm cần xóa
2. Nhấp nút **"🗑️"** (biểu tượng thùng rác)
3. Xác nhận hành động

> **Lưu ý**: Xóa nhóm sẽ **không xóa** người dùng trong nhóm đó

### 3. Quản lý Nhóm Thông tin (Field Groups)

#### Mục đích
Nhóm thông tin giúp tổ chức các trường dữ liệu trong form hợp đồng (ví dụ: "Thông tin cá nhân", "Thông tin tài sản").

#### Thêm nhóm thông tin mới
1. Truy cập: **Admin Panel** → **Nhóm Thông tin**
2. Điền thông tin:
   - **Tên nhóm** (ví dụ: "Thông tin khoản vay")
   - **Mã (Slug)** (tùy chọn, ví dụ: "thong-tin-khoan-vay")
   - **Vị trí**: Cột Trái hoặc Cột Phải
   - **Thứ tự**: Số thứ tự hiển thị
3. Nhấp **"Thêm Nhóm"**

#### Chỉnh sửa nhóm thông tin
1. Nhấp vào hàng cần sửa
2. Cập nhật thông tin
3. Nhấp **"Lưu"**

### 4. Quản lý Trường Thông tin (Fields)

#### Thêm trường mới
1. Truy cập: **Admin Panel** → **Trường Thông tin**
2. Điền thông tin:
   - **Nhãn hiển thị** (ví dụ: "Số tiền vay")
   - **Key** (ví dụ: "so_tien_vay")
   - **Loại dữ liệu**: Văn bản, Số, Ngày, Checkbox
   - **Nhóm**: Chọn nhóm thông tin
   - **Độ rộng**: 1-12 (theo hệ thống grid)
3. Tùy chọn:
   - ☑️ **Tách nghìn**: Hiển thị số với dấu phẩy (1,000,000)
   - ☑️ **Hiện chữ**: Hiển thị số bằng chữ
4. Nhấp **"Thêm"**

#### Sao chép trường
1. Nhấp nút **"Copy"** ở hàng cần sao chép
2. Form sẽ tự động điền thông tin
3. Chỉnh sửa tên và key
4. Nhấp **"Thêm"**

### 5. Quản lý Vai trò (Roles)

#### Thêm vai trò mới
1. Truy cập: **Admin Panel** → **Vai trò**
2. Điền thông tin:
   - **Tên vai trò** (ví dụ: "Người thừa kế")
   - **Mã định danh** (ví dụ: "nguoi_thua_ke")
   - **Mô tả** (tùy chọn)
   - **Quan hệ** (ví dụ: "OWNER", "BENEFICIARY")
3. Nhấp **"Thêm Vai trò"**

> **Lưu ý**: Vai trò hệ thống (có biểu tượng 🔒) không thể xóa

### 6. Nhật ký Hệ thống (Audit Log)

#### Xem nhật ký
- Truy cập: **Admin Panel** → **Quản lý Truy cập** → Tab **"Nhật ký"**

#### Thông tin hiển thị
- **Người dùng**: Ai thực hiện hành động
- **Hành động**: CREATE, UPDATE, DELETE
- **Đối tượng**: User, Group, Field, etc.
- **Thời gian**: Ngày giờ thực hiện
- **Chi tiết**: Thông tin thay đổi (JSON)

#### Tìm kiếm nhật ký
- Sử dụng ô **"Tìm theo username, hành động..."**
- Nhập username hoặc loại hành động để lọc

## Phân quyền

### Các cấp độ quyền

#### 1. Superuser (🛡️)
- Toàn quyền trên hệ thống
- Bypass mọi kiểm tra quyền hạn
- Không thể bị xóa hoặc hạ quyền bởi Admin thường

#### 2. Staff (Admin)
- Truy cập Admin Panel
- Quản lý người dùng, nhóm, quyền hạn
- Không thể chỉnh sửa Superuser

#### 3. User (Người dùng thường)
- Không truy cập được Admin Panel
- Chỉ sử dụng các chức năng cơ bản

### Quyền hạn chi tiết

| Quyền | Mô tả |
|-------|-------|
| `view_user` | Xem danh sách người dùng |
| `add_user` | Thêm người dùng mới |
| `change_user` | Chỉnh sửa thông tin người dùng |
| `delete_user` | Xóa người dùng |
| `view_group` | Xem danh sách nhóm |
| `add_group` | Tạo nhóm mới |
| `change_group` | Chỉnh sửa nhóm |
| `delete_group` | Xóa nhóm |

## Mẹo & Thủ thuật

### Tìm kiếm nhanh
- Sử dụng phím tắt `Ctrl + F` trong danh sách
- Nhập từ khóa vào ô tìm kiếm để lọc

### Sắp xếp danh sách
- Nhấp vào tiêu đề cột để sắp xếp
- Nhấp lại để đảo ngược thứ tự

### Thay đổi kích thước cột
- Kéo thanh phân cách giữa các pane để điều chỉnh

### Làm mới dữ liệu
- Nhấn `F5` hoặc reload trang để cập nhật dữ liệu mới nhất

## Xử lý sự cố

### Không thấy menu Admin Panel
**Nguyên nhân**: Tài khoản chưa có quyền Admin

**Giải pháp**: 
1. Liên hệ Superuser để được cấp quyền
2. Kiểm tra trong **Profile** → **Quyền hạn** xem có quyền `is_staff`

### Không thể xóa người dùng
**Nguyên nhân**: Người dùng là Superuser hoặc bạn không có quyền

**Giải pháp**:
1. Kiểm tra xem người dùng có biểu tượng 🛡️ không
2. Liên hệ Superuser nếu cần xóa tài khoản đặc biệt

### Lỗi khi lưu thay đổi
**Nguyên nhân**: Dữ liệu không hợp lệ hoặc trùng lặp

**Giải pháp**:
1. Kiểm tra các trường bắt buộc đã điền đầy đủ
2. Đảm bảo Username/Email không trùng với tài khoản khác
3. Kiểm tra định dạng email hợp lệ

### Mất kết nối
**Nguyên nhân**: Session hết hạn hoặc mất kết nối server

**Giải pháp**:
1. Reload trang (F5)
2. Đăng nhập lại nếu cần
3. Kiểm tra kết nối mạng

## Bảo mật

### Nguyên tắc quan trọng

1. **Không chia sẻ tài khoản Admin**
   - Mỗi người nên có tài khoản riêng
   - Tránh dùng chung username/password

2. **Thay đổi mật khẩu định kỳ**
   - Đổi mật khẩu ít nhất 3 tháng/lần
   - Sử dụng mật khẩu mạnh (chữ hoa, chữ thường, số, ký tự đặc biệt)

3. **Cẩn thận khi xóa dữ liệu**
   - Kiểm tra kỹ trước khi xóa
   - Hành động xóa không thể hoàn tác

4. **Kiểm tra Audit Log thường xuyên**
   - Theo dõi các hoạt động bất thường
   - Phát hiện truy cập trái phép

## Hỗ trợ

Nếu gặp vấn đề khi sử dụng Admin Panel:

1. Kiểm tra tài liệu này trước
2. Liên hệ bộ phận IT/Hỗ trợ kỹ thuật
3. Báo cáo lỗi qua email: support@vietbank.com

---

**Phiên bản tài liệu**: 1.0  
**Cập nhật lần cuối**: 18/01/2026

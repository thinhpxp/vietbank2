# Hướng dẫn Quản lý Tài khoản

## Giới thiệu

Tài liệu này hướng dẫn bạn cách quản lý tài khoản cá nhân trong hệ thống Vietbank Contract App, bao gồm cập nhật thông tin, đổi mật khẩu, và xem quyền hạn.

## Truy cập Trang Quản lý Tài khoản

### Cách 1: Từ Navbar
1. Đăng nhập vào hệ thống
2. Nhấp vào **tên của bạn** trên thanh điều hướng (góc phải trên)
3. Bạn sẽ được chuyển đến trang **"Quản lý Tài khoản"**

### Cách 2: Trực tiếp qua URL
- Truy cập: `http://localhost:8080/profile`

## Các chức năng

### 1. Xem Thông tin Cá nhân

Trang quản lý tài khoản hiển thị:
- **Username**: Tên đăng nhập (không thể thay đổi)
- **Họ và tên**: Tên đầy đủ của bạn
- **Email**: Địa chỉ email
- **Số điện thoại**: Số liên lạc
- **Nơi làm việc**: Chi nhánh/Văn phòng
- **Phòng ban**: Bộ phận công tác

### 2. Cập nhật Thông tin Cá nhân

#### Các trường có thể chỉnh sửa
- ✅ Họ và tên
- ✅ Email
- ✅ Số điện thoại
- ✅ Nơi làm việc
- ✅ Phòng ban

#### Các trường KHÔNG thể chỉnh sửa
- ❌ Username (tên đăng nhập)

#### Hướng dẫn cập nhật
1. Nhấp vào ô thông tin cần sửa
2. Nhập thông tin mới
3. Nhấp nút **"💾 Cập nhật thông tin"**
4. Chờ thông báo xác nhận thành công

> **Lưu ý**: 
> - Email phải đúng định dạng (ví dụ: `ten@vietbank.com`)
> - Số điện thoại nên có 10-11 chữ số

### 3. Đổi Mật khẩu

#### Yêu cầu bảo mật
- Phải nhập **mật khẩu cũ** để xác thực
- Mật khẩu mới phải:
  - Tối thiểu **8 ký tự**
  - Khác với mật khẩu cũ
  - Khuyến nghị: Kết hợp chữ hoa, chữ thường, số, ký tự đặc biệt

#### Hướng dẫn đổi mật khẩu
1. Cuộn xuống phần **"Đổi mật khẩu"**
2. Nhập **Mật khẩu hiện tại**
3. Nhập **Mật khẩu mới**
4. Nhập lại **Xác nhận mật khẩu mới** (phải giống mật khẩu mới)
5. Nhấp nút **"🔒 Đổi mật khẩu"**
6. Chờ thông báo xác nhận

> **Mẹo tạo mật khẩu mạnh**:
> - Sử dụng cụm từ dễ nhớ: `VietBank@2026!`
> - Kết hợp số và ký tự đặc biệt: `MyP@ssw0rd123`
> - Tránh dùng thông tin cá nhân (tên, ngày sinh)

#### Xử lý lỗi khi đổi mật khẩu

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| "Mật khẩu cũ không đúng" | Nhập sai mật khẩu hiện tại | Kiểm tra lại mật khẩu cũ |
| "Mật khẩu mới quá ngắn" | Mật khẩu < 8 ký tự | Nhập mật khẩu dài hơn |
| "Mật khẩu không khớp" | Xác nhận mật khẩu khác mật khẩu mới | Nhập lại cho khớp |

### 4. Xem Quyền hạn & Nhóm

#### Thông tin hiển thị
- **Vai trò**: Staff, Superuser, hoặc User thường
- **Nhóm**: Các nhóm bạn thuộc về (ví dụ: "soạn thảo", "kế toán")
- **Quyền hạn**: Danh sách quyền cụ thể (nếu có)

#### Ý nghĩa các vai trò

| Vai trò | Mô tả | Quyền hạn |
|---------|-------|-----------|
| **Superuser** 🛡️ | Quản trị viên cao nhất | Toàn quyền trên hệ thống |
| **Staff** | Quản trị viên | Truy cập Admin Panel |
| **User** | Người dùng thường | Sử dụng chức năng cơ bản |

> **Lưu ý**: Bạn **không thể tự thay đổi** quyền hạn của mình. Liên hệ Admin nếu cần thêm quyền.

## Đăng ký Tài khoản Mới

### Hướng dẫn đăng ký

1. Truy cập trang đăng ký: `http://localhost:8080/register`
2. Điền đầy đủ thông tin:
   - **Username** (bắt buộc): Tên đăng nhập duy nhất
   - **Email** (bắt buộc): Địa chỉ email hợp lệ
   - **Mật khẩu** (bắt buộc): Tối thiểu 8 ký tự
   - **Họ và tên** (bắt buộc)
   - **Số điện thoại** (tùy chọn)
   - **Nơi làm việc** (tùy chọn)
   - **Phòng ban** (tùy chọn)
3. Nhấp nút **"Đăng ký"**
4. Chờ thông báo xác nhận
5. Đăng nhập bằng tài khoản vừa tạo

### Nhóm mặc định
- Tài khoản mới sẽ **tự động** được thêm vào nhóm **"soạn thảo"**
- Bạn có thể yêu cầu Admin thêm vào nhóm khác nếu cần

### Lỗi thường gặp khi đăng ký

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| "Username đã tồn tại" | Tên đăng nhập bị trùng | Chọn username khác |
| "Email đã được sử dụng" | Email đã đăng ký | Sử dụng email khác hoặc đăng nhập |
| "Mật khẩu quá yếu" | Mật khẩu không đủ mạnh | Tăng độ phức tạp mật khẩu |

## Bảo mật Tài khoản

### Nguyên tắc quan trọng

#### 1. Bảo vệ mật khẩu
- ✅ Sử dụng mật khẩu mạnh, duy nhất
- ✅ Đổi mật khẩu định kỳ (3-6 tháng/lần)
- ❌ Không chia sẻ mật khẩu với người khác
- ❌ Không dùng chung mật khẩu với hệ thống khác

#### 2. Bảo vệ thông tin cá nhân
- Kiểm tra thông tin định kỳ
- Cập nhật email và SĐT khi thay đổi
- Báo ngay cho Admin nếu phát hiện bất thường

#### 3. Đăng xuất an toàn
- Luôn **đăng xuất** khi rời khỏi máy tính
- Không lưu mật khẩu trên trình duyệt công cộng

### Phát hiện truy cập trái phép

Dấu hiệu cảnh báo:
- Thông tin tài khoản bị thay đổi mà bạn không biết
- Nhận email thông báo đổi mật khẩu không do bạn thực hiện
- Không thể đăng nhập bằng mật khẩu cũ

**Hành động ngay**:
1. Thử đổi mật khẩu ngay lập tức
2. Liên hệ Admin/IT Support
3. Kiểm tra email và SĐT có bị thay đổi không

## Câu hỏi Thường gặp (FAQ)

### Q: Tôi quên mật khẩu, làm sao để lấy lại?
**A**: Liên hệ Admin hoặc bộ phận IT để được reset mật khẩu. Hiện tại hệ thống chưa hỗ trợ tự động reset qua email.

### Q: Tại sao tôi không thể thay đổi Username?
**A**: Username là định danh duy nhất của tài khoản, không thể thay đổi để đảm bảo tính toàn vẹn dữ liệu. Nếu cần đổi, liên hệ Admin để tạo tài khoản mới.

### Q: Làm sao để xem tôi thuộc nhóm nào?
**A**: Truy cập trang **Quản lý Tài khoản** → Phần **"Quyền hạn & Nhóm"** sẽ hiển thị danh sách nhóm bạn thuộc về.

### Q: Tôi có thể tự thêm mình vào nhóm khác không?
**A**: Không. Chỉ Admin mới có quyền thêm/xóa người dùng khỏi nhóm. Liên hệ Admin nếu cần thay đổi.

### Q: Email có bắt buộc phải là email Vietbank không?
**A**: Không bắt buộc, nhưng khuyến nghị sử dụng email công ty để dễ quản lý và liên lạc.

### Q: Tôi có thể có nhiều tài khoản không?
**A**: Không khuyến nghị. Mỗi người nên chỉ có một tài khoản để dễ quản lý và theo dõi hoạt động.

## Liên hệ Hỗ trợ

Nếu gặp vấn đề với tài khoản:

- **Email**: support@vietbank.com
- **Hotline**: 1900-xxxx
- **Liên hệ Admin**: Qua Admin Panel hoặc email trực tiếp

---

**Phiên bản tài liệu**: 1.0  
**Cập nhật lần cuối**: 18/01/2026

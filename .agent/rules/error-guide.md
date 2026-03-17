---
trigger: always_on
---

# Quy chuẩn Xử lý và Hiển thị Lỗi (Error Handling Standards)

Để đảm bảo trải nghiệm người dùng đồng nhất và hỗ trợ kỹ thuật hiệu quả, hệ thống áp dụng cơ chế xử lý lỗi tập trung.

### 1. Cơ chế hiển thị Duy nhất (Single Modal Policy)
- **Ưu tiên Toàn cục (Global First)**: Chỉ sử dụng **duy nhất một** linh kiện `ConfirmModal` tại `App.vue` để hiển thị các thông báo lỗi, thành công, hoặc cảnh báo mang tính chặn (blocking).
- **Cấm Modal cục bộ**: Các component không được tự khai báo `<ConfirmModal>` cho mục đích hiển thị lỗi (trừ trường hợp đặc biệt cần tương tác phức tạp bên trong modal).
- **Sử dụng Event Bus**: Việc hiển thị lỗi phải thông qua hàm `showErrorDialog` hoặc mixin `errorHandlingMixin`. Các hàm này sẽ phát sự kiện về `App.vue`.

### 2. Yêu cầu về Nội dung và Metadata
Mọi thông báo lỗi hiển thị cho người dùng **phải** bao gồm:
- **Thông điệp thân thiện**: Được dịch sang tiếng Việt (sử dụng `i18n.js`).
- **Mã lỗi (ErrorCode)**: Giúp định danh loại lỗi (ví dụ: `HTTP_403`, `VALIDATION_ERROR`).
- **Dấu thời gian (Timestamp)**: Luôn hiển thị thời gian xảy ra lỗi (định dạng `HH:mm:ss DD/MM/YYYY`) để phục vụ đối chiếu logs.
- **Chi tiết kỹ thuật (Details)**: Các thông tin nhạy cảm hoặc kỹ thuật cao (JSON response, stack trace) phải được ẩn trong phần "Chi tiết kỹ thuật" (mặc định đóng).

### 3. Phân vùng xử lý (Responsibility)
- **Tầng API (api.js)**: Tự động bắt và hiển thị lỗi hạ tầng (401, 403, 500, 503, 504).
- **Tầng Component**: Chỉ xử lý các lỗi nghiệp vụ đặc thù. Khi catch được lỗi, PHẢI gọi `showError(error)` để đẩy lên Global Modal.

### 4. Chống lặp và Chồng chéo
- **Debounce**: Mọi yêu cầu hiển thị lỗi phải đi qua cơ chế lọc (debounce) ít nhất 500ms cho cùng một loại lỗi.
- **Access Control**: Các lỗi 403 (Forbidden) chỉ được hiển thị 1 lần duy nhất từ Global Handler.
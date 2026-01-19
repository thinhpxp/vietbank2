# Hướng dẫn Xử lý Lỗi với ConfirmModal

## Tổng quan

Hệ thống xử lý lỗi đã được nâng cấp để hiển thị thông tin chi tiết, giúp developer và user dễ dàng chuẩn đoán vấn đề.

## Tính năng Mới của ConfirmModal

### 1. Các Props Mới

| Prop | Kiểu | Mặc định | Mô tả |
|------|------|---------|-------|
| `mode` | String | `'confirm'` | `'alert'` (1 nút) hoặc `'confirm'` (2 nút) |
| `type` | String | `'warning'` | `'warning'`, `'error'`, `'success'`, `'info'` |
| `errorCode` | String | `''` | Mã lỗi (VD: "ERR_001", "HTTP_404") |
| `details` | String | `''` | Chi tiết kỹ thuật (stack trace, JSON response) |
| `showTimestamp` | Boolean | `false` | Hiển thị thời gian xảy ra lỗi |
| `closeOnOverlay` | Boolean | `false` | Đóng khi click vào overlay |
| `cancelText` | String | `'Hủy'` | Text nút hủy |

### 2. Các Loại Dialog

#### Error Dialog (Lỗi)
```vue
<ConfirmModal
  :visible="showError"
  type="error"
  mode="alert"
  title="Lỗi khi tải dữ liệu"
  message="Không thể kết nối đến server"
  errorCode="NETWORK_ERROR"
  :details="errorDetails"
  :showTimestamp="true"
  confirmText="Đóng"
  @confirm="showError = false"
  @cancel="showError = false"
/>
```

#### Warning Dialog (Cảnh báo)
```vue
<ConfirmModal
  :visible="showWarning"
  type="warning"
  mode="confirm"
  title="Xác nhận xóa"
  message="Bạn có chắc chắn muốn xóa người dùng này?"
  confirmText="Xóa"
  cancelText="Hủy"
  @confirm="handleDelete"
  @cancel="showWarning = false"
/>
```

#### Success Dialog (Thành công)
```vue
<ConfirmModal
  :visible="showSuccess"
  type="success"
  mode="alert"
  title="Thành công"
  message="Đã lưu dữ liệu thành công!"
  confirmText="OK"
  @confirm="showSuccess = false"
  @cancel="showSuccess = false"
/>
```

#### Info Dialog (Thông tin)
```vue
<ConfirmModal
  :visible="showInfo"
  type="info"
  mode="alert"
  title="Thông tin"
  message="Hệ thống sẽ bảo trì vào 2h sáng mai"
  confirmText="Đã hiểu"
  @confirm="showInfo = false"
  @cancel="showInfo = false"
/>
```

## Sử dụng Error Handler Utility

### Cách 1: Sử dụng Mixin (Khuyến nghị)

```vue
<template>
  <div>
    <!-- Error Modal -->
    <ConfirmModal
      :visible="showErrorModal"
      type="error"
      mode="alert"
      :title="errorModalTitle"
      :message="errorModalMessage"
      :errorCode="errorModalCode"
      :details="errorModalDetails"
      :showTimestamp="true"
      confirmText="Đóng"
      @confirm="showErrorModal = false"
      @cancel="showErrorModal = false"
    />

    <!-- Success Modal -->
    <ConfirmModal
      :visible="showSuccessModal"
      type="success"
      mode="alert"
      :title="successModalTitle"
      :message="successModalMessage"
      confirmText="OK"
      @confirm="showSuccessModal = false"
      @cancel="showSuccessModal = false"
    />

    <button @click="saveData">Lưu dữ liệu</button>
  </div>
</template>

<script>
import ConfirmModal from '@/components/ConfirmModal.vue';
import { errorHandlingMixin } from '@/utils/errorHandler';
import axios from 'axios';

export default {
  components: { ConfirmModal },
  mixins: [errorHandlingMixin],
  
  methods: {
    async saveData() {
      try {
        await axios.post('/api/users/', this.formData);
        this.showSuccess('Tạo người dùng thành công!');
      } catch (error) {
        this.showError(error, 'Lỗi khi tạo người dùng');
      }
    }
  }
};
</script>
```

### Cách 2: Sử dụng Helper Functions

```vue
<script>
import { showErrorDialog, formatError, logError } from '@/utils/errorHandler';

export default {
  methods: {
    async loadData() {
      try {
        const response = await axios.get('/api/data');
        this.data = response.data;
      } catch (error) {
        // Log error cho debugging
        logError('MyComponent.loadData', error);
        
        // Hiển thị error dialog
        showErrorDialog(this, error, 'Lỗi tải dữ liệu');
      }
    },
    
    handleCustomError() {
      const { message, errorCode, details } = formatError(someError);
      // Sử dụng message, errorCode, details theo ý muốn
    }
  }
};
</script>
```

## Ví dụ Thực tế

### Ví dụ 1: Xử lý lỗi API với thông tin chi tiết

```javascript
async createUser() {
  try {
    await axios.post('/api/users/', {
      username: this.username,
      email: this.email
    });
    this.showSuccess('Tạo người dùng thành công!');
  } catch (error) {
    // Error sẽ tự động format và hiển thị:
    // - Message: "Username đã tồn tại"
    // - Error Code: "HTTP_400"
    // - Details: JSON response từ server
    this.showError(error, 'Lỗi khi tạo người dùng');
  }
}
```

### Ví dụ 2: Validation Error

```javascript
validateForm() {
  if (!this.username) {
    this.showWarning('Vui lòng nhập username', 'Thiếu thông tin');
    return false;
  }
  
  if (this.password.length < 8) {
    this.showWarning(
      'Mật khẩu phải có ít nhất 8 ký tự',
      'Mật khẩu không hợp lệ'
    );
    return false;
  }
  
  return true;
}
```

### Ví dụ 3: Network Error

```javascript
async fetchData() {
  try {
    const response = await axios.get('/api/data');
    this.data = response.data;
  } catch (error) {
    // Nếu là network error, sẽ hiển thị:
    // - Message: "Không thể kết nối đến server..."
    // - Error Code: "NETWORK_ERROR"
    // - Details: Request URL và method
    this.showError(error, 'Lỗi kết nối');
  }
}
```

## Format của Error Details

Error details sẽ được format thành JSON dễ đọc:

```json
{
  "status": 400,
  "statusText": "Bad Request",
  "url": "/api/users/",
  "method": "POST",
  "data": {
    "username": ["Username đã tồn tại"],
    "email": ["Email không hợp lệ"]
  }
}
```

## Best Practices

### ✅ Nên làm

1. **Sử dụng mixin cho consistency**
   ```javascript
   mixins: [errorHandlingMixin]
   ```

2. **Cung cấp context rõ ràng trong title**
   ```javascript
   this.showError(error, 'Lỗi khi tạo người dùng');
   // Tốt hơn: this.showError(error, 'Lỗi');
   ```

3. **Log error cho debugging**
   ```javascript
   logError('ComponentName.methodName', error);
   ```

4. **Sử dụng đúng type cho từng trường hợp**
   - `error`: Lỗi hệ thống, lỗi API
   - `warning`: Cảnh báo, xác nhận hành động nguy hiểm
   - `success`: Thông báo thành công
   - `info`: Thông tin chung

### ❌ Không nên làm

1. **Không hardcode error message**
   ```javascript
   // Không tốt
   this.showError('Lỗi', 'Lỗi');
   
   // Tốt
   this.showError(error, 'Lỗi khi tải dữ liệu');
   ```

2. **Không bỏ qua error details**
   ```javascript
   // Không tốt
   catch (error) {
     this.showError('Có lỗi xảy ra');
   }
   
   // Tốt
   catch (error) {
     this.showError(error, 'Lỗi khi lưu');
   }
   ```

3. **Không dùng alert() native**
   ```javascript
   // Không tốt
   alert('Lỗi!');
   
   // Tốt
   this.showError(error, 'Lỗi');
   ```

## Tính năng Chi tiết Kỹ thuật

### Expandable Details
- User có thể click "▶ Chi tiết kỹ thuật" để xem thông tin debug
- Details được hiển thị trong `<pre>` tag, dễ đọc
- Tự động scroll nếu nội dung dài

### Timestamp
- Hiển thị thời gian xảy ra lỗi (format Việt Nam)
- Chỉ hiển thị khi `showTimestamp={true}` và `type="error"`
- Hữu ích cho error tracking

### Type-specific Styling
- Mỗi type có màu icon và button riêng
- Error: Đỏ (❌)
- Warning: Cam (⚠️)
- Success: Xanh lá (✅)
- Info: Xanh dương (ℹ️)

## Migration từ alert() native

### Trước
```javascript
try {
  await saveData();
} catch (error) {
  alert('Lỗi khi lưu: ' + error.message);
}
```

### Sau
```javascript
try {
  await saveData();
} catch (error) {
  this.showError(error, 'Lỗi khi lưu dữ liệu');
}
```

## Tài nguyên

- **Component**: `frontend/src/components/ConfirmModal.vue`
- **Utility**: `frontend/src/utils/errorHandler.js`
- **Design System**: Xem `design-system.md` cho button styles

---

**Phiên bản**: 2.0  
**Cập nhật**: 19/01/2026

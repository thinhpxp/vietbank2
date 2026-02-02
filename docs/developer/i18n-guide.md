# Hướng dẫn sử dụng Hệ thống Dịch (i18n) Frontend

Hệ thống dịch được xây dựng để giúp bạn chủ động cấu trúc lại các nhãn (labels) hoặc mã hệ thống (system codes) từ Tiếng Anh sang Tiếng Việt mà không cần can thiệp vào Logic của Backend.

## 1. Vị trí tệp tin
Mọi từ vựng được quản lý tập trung tại:  
`frontend/src/utils/i18n.js`

## 2. Cách thêm từ mới vào Từ điển
Mở file `i18n.js`, bạn sẽ thấy đối tượng `dictionary`. Để Việt hóa một mã mới, hãy thêm một dòng theo cú pháp:  
`'MA_TIENG_ANH': 'Nội dung Tiếng Việt',`

**Ví dụ:**
```javascript
const dictionary = {
    // ... các từ cũ
    'CONTRACT_MOI': 'Hợp đồng mới thêm',
    'STATUS_PENDING': 'Đang chờ duyệt',
};
```
*Lưu ý: Hệ thống được thiết kế để tự động chuyển Key sang Chữ hoa (Uppercase) khi tra cứu, nên bạn nên đặt Key viết hoa để đảm bảo tính nhất quán.*

## 3. Cách sử dụng trong giao diện (Vue Component)

### Trong thẻ Template (HTML)
Bạn có thể sử dụng trực tiếp hàm `$t(key)` nhờ vào việc đã đăng ký Global Plugin.
```html
<span>{{ $t(item.role) }}</span>
```

### Trong Script (JS)
Nếu cần dịch bên trong phần xử lý Logic, hãy import hàm `translate` từ tiện ích:
```javascript
import { translate } from '@/utils/i18n';

const vLabel = translate('PERSON'); // Trả về "Cá nhân"
```

## 4. Nguyên tắc hoạt động
1.  Nhận vào một chuỗi (Key).
2.  Chuyển chuỗi đó thành Chữ hoa.
3.  Tìm kiếm trong `dictionary`.
4.  Nếu tìm thấy: Trả về giá trị Tiếng Việt.
5.  Nếu không tìm thấy: Trả về chính chuỗi ban đầu (để tránh mất dữ liệu hiển thị).

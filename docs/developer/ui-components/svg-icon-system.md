# Tài liệu Hệ thống Icon SVG

## Tổng quan

Ứng dụng Vietbank Contract sử dụng hệ thống icon SVG tập trung, cung cấp các biểu tượng nhất quán, có thể tùy chỉnh và hiệu suất cao trong toàn bộ ứng dụng. Hệ thống này thay thế các icon dạng emoji bằng đồ họa vector có thể mở rộng (SVG), dễ dàng tùy biến qua CSS.

## Bắt đầu Nhanh

### Sử dụng Cơ bản

```vue
<template>
  <button class="btn-action btn-primary">
    <SvgIcon name="plus" size="sm" /> Thêm mới
  </button>
</template>
```

Component `SvgIcon` đã được đăng ký toàn cục, bạn có thể sử dụng ở bất kỳ đâu mà không cần import.

## API Component

### Props (Thuộc tính)

| Prop | Kiểu | Mặc định | Mô tả |
|------|------|---------|-------|
| `name` | String | *bắt buộc* | Tên icon (xem [Danh sách Icon](#danh-sách-icon)) |
| `size` | String \| Number | `'md'` | Kích thước định sẵn (`xs`, `sm`, `md`, `lg`, `xl`) hoặc giá trị pixel tùy chỉnh |
| `stroke` | String | `'currentColor'` | Màu nét vẽ (mặc định kế thừa từ phần tử cha) |
| `strokeWidth` | String \| Number | `2` | Độ dày nét vẽ (pixel) |
| `customClass` | String | `''` | Class CSS bổ sung |

### Bảng Kích thước

| Kích thước | Pixel | Trường hợp sử dụng |
|------------|-------|-------------------|
| `xs` | 14px | Icon trong dòng text |
| `sm` | 16px | Icon trong button, link navbar |
| `md` | 20px | Kích thước mặc định, avatar người dùng |
| `lg` | 24px | Tiêu đề phần |
| `xl` | 32px | Phần hero, button lớn |

## Danh sách Icon

### Điều hướng & Giao diện
- `user` - Icon hồ sơ người dùng
- `users` - Icon nhiều người dùng/nhóm
- `logout` - Icon đăng xuất
- `settings` - Icon cài đặt/cấu hình
- `menu` - Icon menu hamburger
- `folder` - Icon thư mục/danh mục
- `file` - Icon tài liệu/file

### Hành động
- `plus` - Thêm/tạo mới
- `edit` - Chỉnh sửa/sửa đổi
- `trash` - Xóa/loại bỏ
- `save` - Lưu/đĩa mềm
- `copy` - Sao chép/nhân bản
- `download` - Tải xuống
- `upload` - Tải lên

### Trạng thái & Phản hồi
- `check` - Thành công/dấu kiểm
- `x` - Đóng/hủy
- `alert` - Cảnh báo
- `info` - Thông tin
- `lock` - Khóa/bảo mật
- `unlock` - Mở khóa

### Tiện ích
- `search` - Tìm kiếm/kính lúp
- `filter` - Lọc/phễu
- `eye` - Hiển thị/xem
- `eye-off` - Ẩn/không xem
- `shield` - Bảo mật/bảo vệ

### Mũi tên Điều hướng
- `chevron-down` - Chỉ báo dropdown
- `chevron-up` - Chỉ báo thu gọn
- `chevron-left` - Trước/quay lại
- `chevron-right` - Tiếp/tiến

## Tùy biến & Styling

### Kế thừa Màu sắc

Icon tự động kế thừa màu chữ từ phần tử cha:

```vue
<!-- Icon sẽ có màu xanh -->
<button style="color: #4180bf;">
  <SvgIcon name="user" />
</button>

<!-- Icon sẽ có màu trắng (từ btn-primary) -->
<button class="btn-action btn-primary">
  <SvgIcon name="plus" /> Thêm
</button>
```

### Class Màu Định sẵn

Sử dụng class tiện ích cho màu cụ thể:

```vue
<SvgIcon name="check" class="icon-success" />
<SvgIcon name="trash" class="icon-danger" />
<SvgIcon name="alert" class="icon-warning" />
<SvgIcon name="info" class="icon-primary" />
<SvgIcon name="user" class="icon-muted" />
```

### Tùy chỉnh Kích thước

```vue
<!-- Kích thước định sẵn -->
<SvgIcon name="user" size="lg" />

<!-- Kích thước pixel tùy chỉnh -->
<SvgIcon name="settings" :size="28" />
```

### Icon Tương tác

Thêm class `interactive` cho hiệu ứng hover:

```vue
<SvgIcon name="edit" class="interactive" @click="handleEdit" />
```

Điều này thêm:
- Con trỏ pointer
- Animation phóng to khi hover (1.1x)
- Chuyển đổi opacity

## Thực hành Tốt nhất

### ✅ Nên làm

```vue
<!-- Sử dụng biến thể kích thước để đảm bảo nhất quán -->
<SvgIcon name="user" size="sm" />

<!-- Để icon kế thừa màu từ phần tử cha -->
<button class="btn-danger">
  <SvgIcon name="trash" /> Xóa
</button>

<!-- Sử dụng tên icon có ngữ nghĩa -->
<SvgIcon name="logout" /> <!-- Ý định rõ ràng -->
```

### ❌ Không nên làm

```vue
<!-- Tránh inline style cho kích thước -->
<SvgIcon name="user" style="width: 18px;" />

<!-- Không ghi đè màu stroke trừ khi cần thiết -->
<SvgIcon name="user" stroke="#ff0000" />

<!-- Không dùng tên chung chung -->
<SvgIcon name="icon1" /> <!-- Mục đích không rõ -->
```

## Mẫu Thường gặp

### Button với Icon

```vue
<button class="btn-action btn-primary">
  <SvgIcon name="plus" size="sm" /> Tạo mới
</button>
```

### Button chỉ có Icon

```vue
<button class="btn-icon danger">
  <SvgIcon name="trash" size="sm" />
</button>
```

### Link Navbar với Icon

```vue
<router-link to="/settings">
  <SvgIcon name="settings" size="sm" /> Cài đặt
</router-link>
```

### Chỉ báo Trạng thái

```vue
<span class="status-badge">
  <SvgIcon name="check" size="xs" class="icon-success" />
  Hoạt động
</span>
```

## Thêm Icon Mới

Để thêm icon mới vào hệ thống:

1. **Tìm hoặc tạo dữ liệu path SVG** (khuyến nghị viewBox 24x24)
2. **Mở file** `src/components/common/SvgIcon.vue`
3. **Thêm vào object `icons`**:

```javascript
const icons = {
  // ... các icon hiện có
  
  'ten-icon-cua-ban': () => h('g', [
    h('path', { d: 'M12 2L2 7l10 5 10-5-10-5z' }),
    h('path', { d: 'M2 17l10 5 10-5' })
  ]),
};
```

4. **Sử dụng path dạng stroke** khi có thể (không phải fill) để đảm bảo nhất quán
5. **Kiểm tra** trong các ngữ cảnh khác nhau (button, navbar, kích thước khác nhau)

### Hướng dẫn Thiết kế Icon

- **Độ dày nét**: Mặc định 2px
- **ViewBox**: 24x24 (chuẩn)
- **Phong cách**: Outline/stroke (không filled) để nhất quán
- **Đơn giản**: Tránh path quá phức tạp
- **Khả năng tiếp cận**: Sử dụng tên có ngữ nghĩa

## Kiến trúc CSS

Các style icon được tập trung trong `src/assets/icons.css`:

```css
/* Style cơ bản */
.svg-icon { ... }

/* Biến thể kích thước */
.icon-xs { width: 14px; height: 14px; }
.icon-sm { width: 16px; height: 16px; }
/* ... */

/* Tiện ích màu sắc */
.icon-primary { color: var(--color-primary); }
.icon-success { color: var(--color-success); }
/* ... */

/* Trạng thái tương tác */
.svg-icon.interactive:hover { ... }
```

## Cân nhắc Hiệu suất

- **Không phụ thuộc bên ngoài**: Icon được nhúng trong component
- **Hỗ trợ tree-shaking**: Chỉ icon được sử dụng mới được đưa vào bundle
- **Điều khiển bằng CSS**: Thay đổi màu và kích thước không cần re-render
- **Nhẹ**: ~2KB cho toàn bộ hệ thống icon

## Di chuyển từ Emoji

Nếu bạn đang thay thế icon emoji:

| Emoji | Tên Icon SVG |
|-------|--------------|
| 👤 | `user` |
| ⚙️ | `settings` |
| 🗂️ | `folder` |
| 📝 | `edit` |
| 🗑️ | `trash` |
| ➕ | `plus` |
| 💾 | `save` |
| 📋 | `copy` |
| 🔒 | `lock` |
| 🔓 | `unlock` |

**Ví dụ di chuyển:**

```vue
<!-- Trước -->
<button>🗑️ Xóa</button>

<!-- Sau -->
<button class="btn-action btn-danger">
  <SvgIcon name="trash" size="sm" /> Xóa
</button>
```

## Xử lý Sự cố

### Icon không hiển thị

1. Kiểm tra tên icon có tồn tại trong object `icons` không
2. Xác minh component đã được import (nên là global)
3. Kiểm tra console trình duyệt để tìm lỗi

### Màu icon không thay đổi

1. Đảm bảo bạn không ghi đè prop `stroke`
2. Kiểm tra thuộc tính CSS `color` của phần tử cha
3. Xác minh `currentColor` không bị ghi đè

### Kích thước icon không nhất quán

1. Sử dụng biến thể kích thước định sẵn (`xs`, `sm`, `md`, `lg`, `xl`)
2. Tránh trộn lẫn kích thước pixel tùy chỉnh với biến thể
3. Kiểm tra các quy tắc CSS xung đột

## Hỗ trợ

Nếu có câu hỏi hoặc vấn đề với hệ thống icon:
- Kiểm tra tài liệu này trước
- Xem lại source code `src/components/common/SvgIcon.vue`
- Liên hệ team phát triển

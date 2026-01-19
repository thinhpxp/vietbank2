# Hướng dẫn Design System

## Giới thiệu

Design System của Vietbank Contract App đảm bảo tính nhất quán về mặt hình ảnh, khả năng bảo trì và hiệu quả phát triển trong toàn bộ ứng dụng. Tài liệu này trình bày các nguyên tắc cốt lõi, component và mẫu sử dụng.

## Design Tokens (Biến Thiết kế)

Design tokens là nền tảng của hệ thống thiết kế. Chúng được định nghĩa trong `src/assets/tokens.scss` và có sẵn trong toàn bộ ứng dụng.

### Màu sắc

```scss
// Màu chính
--color-primary: #2c3e50;      // Xanh xám đậm (navbar, header)
--color-secondary: #34495e;    // Xanh xám nhạt hơn
--color-accent: #3498db;       // Xanh sáng (link, highlight)

// Màu ngữ nghĩa
--color-success: #27ae60;      // Xanh lá (thành công)
--color-danger: #e74c3c;       // Đỏ (lỗi, xóa)
--color-warning: #f39c12;      // Cam (cảnh báo)
--color-info: #3498db;         // Xanh (thông tin)

// Màu trung tính
--color-light: #ecf0f1;        // Xám nhạt (nền)
--color-dark: #2c3e50;         // Tối (text)
--color-text-muted: #7f8c8d;  // Text mờ

// UI cụ thể
--admin-panel-bg: #4180bf;     // Nền admin panel
```

### Khoảng cách

```scss
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 12px;
--spacing-lg: 16px;
--spacing-xl: 24px;
--spacing-2xl: 32px;
```

### Bo góc

```scss
--radius-sm: 4px;
--radius-md: 6px;   // Chuẩn cho input và button
--radius-lg: 8px;
--radius-xl: 12px;
```

## Hệ thống Button

### Class Button Cơ bản

Tất cả button nên sử dụng class `.btn-action`:

```vue
<button class="btn-action">Button cơ bản</button>
```

**Thông số:**
- Chiều cao: `32px` (cố định)
- Padding: `0 12px`
- Bo góc: `6px`
- Font weight: `600`
- Font size: `0.9rem`
- Display: `inline-flex` với `align-items: center`
- Khoảng cách icon-text: `5px`

### Các Biến thể Button

#### Button Chính (Primary)
```vue
<button class="btn-action btn-primary">
  <SvgIcon name="plus" size="sm" /> Tạo mới
</button>
```
- Nền: `#3498db`, Chữ: `white`
- Dùng cho: Hành động chính, CTA

#### Button Thành công (Success)
```vue
<button class="btn-action btn-success">
  <SvgIcon name="save" size="sm" /> Lưu
</button>
```
- Nền: `#27ae60`, Chữ: `white`
- Dùng cho: Xác nhận, lưu

#### Button Nguy hiểm (Danger)
```vue
<button class="btn-action btn-danger">
  <SvgIcon name="trash" size="sm" /> Xóa
</button>
```
- Nền: `#e74c3c`, Chữ: `white`
- Dùng cho: Hành động phá hủy, xóa

#### Button Phụ (Secondary)
```vue
<button class="btn-action btn-secondary">Hủy</button>
```
- Nền: `#95a5a6`, Chữ: `white`
- Dùng cho: Hành động phụ, hủy

#### Button Khóa/Mở khóa
```vue
<button class="btn-action btn-lock">
  <SvgIcon name="lock" size="sm" /> Khóa
</button>

<button class="btn-action btn-unlock">
  <SvgIcon name="unlock" size="sm" /> Mở khóa
</button>
```
- Lock: Nền cam (`#fdf6e3` bg, `#e67e22` text)
- Unlock: Nền xanh lá (`#e8f5e9` bg, `#2e7d32` text)

### Button với Icon

**Thực hành tốt:**
```vue
<!-- Icon bên trái (khuyến nghị) -->
<button class="btn-action btn-primary">
  <SvgIcon name="plus" size="sm" /> Thêm
</button>

<!-- Chỉ icon (dùng btn-icon) -->
<button class="btn-icon danger">
  <SvgIcon name="trash" size="sm" />
</button>
```

## Form Controls

### Input Chuẩn
```vue
<input type="text" class="admin-input" placeholder="Nhập text..." />
```

**Thông số:**
- Chiều cao: `32px`
- Padding: `6px 10px`
- Border: `1px solid #ddd`
- Bo góc: `6px`
- Font size: `0.9rem`

### Bố cục Form

#### Admin Row (Ngang)
```vue
<div class="admin-row">
  <input class="admin-input" placeholder="Trường 1" />
  <input class="admin-input" placeholder="Trường 2" />
  <button class="btn-action btn-primary">Gửi</button>
</div>
```

**Thông số:**
- Display: `flex`
- Gap: `10px`
- Flex-wrap: `wrap`
- Align-items: `center`

#### Form Group (Dọc)
```vue
<div class="form-group">
  <label>Nhãn trường</label>
  <input class="admin-input" />
</div>
```

## Layout Components

### Page Container
```vue
<div class="page-container">
  <!-- Nội dung trang -->
</div>
```

**Thông số:**
- Max-width: `95%`
- Margin: `0 auto`
- Padding: `20px`
- Background: `white`
- Bo góc: `8px`
- Box-shadow: `0 2px 10px rgba(0, 0, 0, 0.05)`

### Admin Panel
```vue
<div class="admin-panel">
  <h4>Tiêu đề Panel</h4>
  <div class="admin-row">
    <!-- Form controls -->
  </div>
</div>
```

**Thông số:**
- Background: `#4180bf` (xanh)
- Color: `#ffffff` (chữ trắng)
- Padding: `15px`
- Bo góc: `6px`
- Margin-bottom: `20px`

## Class Tiện ích

### Flexbox
```css
.flex          /* display: flex */
.flex-1        /* flex: 1 (mở rộng để lấp đầy) */
.gap-2         /* gap: 8px */
.items-center  /* align-items: center */
```

### Khoảng cách
```css
.mb-2   /* margin-bottom: 8px */
.mb-4   /* margin-bottom: 16px */
.mt-2   /* margin-top: 8px */
.p-2    /* padding: 8px */
```

## Thực hành Tốt nhất

### ✅ Nên làm

1. **Dùng design tokens** thay vì giá trị cứng
   ```vue
   <!-- Tốt -->
   <div style="color: var(--color-primary);">
   
   <!-- Không tốt -->
   <div style="color: #2c3e50;">
   ```

2. **Dùng tên class có ngữ nghĩa**
   ```vue
   <!-- Tốt -->
   <button class="btn-action btn-danger">Xóa</button>
   
   <!-- Không tốt -->
   <button class="red-button">Xóa</button>
   ```

3. **Dùng SVG icons** thay vì emoji
   ```vue
   <!-- Tốt -->
   <SvgIcon name="user" size="sm" />
   
   <!-- Không tốt -->
   👤
   ```

### ❌ Không nên làm

1. Không dùng inline styles cho giá trị design token
2. Không tạo style button tùy chỉnh - mở rộng biến thể có sẵn
3. Không trộn lẫn đơn vị spacing - dùng design tokens
4. Không hardcode màu - dùng CSS variables

## Khả năng Tiếp cận (Accessibility)

### Độ tương phản Màu
- Đảm bảo text có tỷ lệ tương phản ít nhất 4.5:1
- Dùng `--color-text-muted` một cách tiết kiệm

### Focus States
- Tất cả phần tử tương tác có focus state rõ ràng
- Không xóa outline mà không cung cấp thay thế

### Điều hướng Bàn phím
- Tất cả button và link có thể truy cập bằng bàn phím
- Dùng HTML ngữ nghĩa (`<button>`, `<a>`, etc.)

## Cấu trúc File

```
src/assets/
├── tokens.scss           # Design tokens
├── common-ui.css         # Component UI chung
├── admin.css             # Style admin
└── icons.css             # Tiện ích SVG icon
```

## Hướng dẫn Di chuyển

### Từ Inline Styles
```vue
<!-- Trước -->
<button style="background: #3498db; color: white; padding: 8px 16px;">
  Click me
</button>

<!-- Sau -->
<button class="btn-action btn-primary">
  Click me
</button>
```

### Từ CSS Tùy chỉnh
```vue
<!-- Trước -->
<button class="my-custom-button">Lưu</button>

<style>
.my-custom-button {
  background: green;
  color: white;
}
</style>

<!-- Sau -->
<button class="btn-action btn-success">
  <SvgIcon name="save" size="sm" /> Lưu
</button>
```

## Tài nguyên

- **Design Tokens**: `src/assets/tokens.scss`
- **Button Styles**: `src/assets/common-ui.css` (dòng 28-120)
- **Form Styles**: `src/assets/admin.css` (dòng 140-180)
- **Hệ thống Icon**: Xem [Tài liệu Hệ thống Icon SVG](./svg-icon-system.md)

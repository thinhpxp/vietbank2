# Khắc phục lỗi Table bị tràn màn hình khi resize column (Excel-like UI)

## 1. Nguyên nhân gốc

### 1.1 Table tự do mở rộng
- Resize column làm tổng width các cột > viewport
- Table không bị giới hạn nên tràn sang phải màn hình

### 1.2 Thiếu scroll container
- Table không được bọc trong container có `overflow-x`
- Browser ưu tiên mở rộng layout thay vì tạo scroll

### 1.3 Resize trực tiếp lên `<th>`
- Resize chỉ tác động width column
- Không đồng bộ lại tổng width của table

---

## 2. Nguyên tắc chuẩn (Excel / Notion / Airtable)

> Resize column → Table rộng hơn → Xuất hiện **horizontal scroll**, không phá layout

---

## 3. Giải pháp A (Khuyến nghị – Chuẩn Excel)

### HTML
```html
<div class="table-scroll-wrapper">
  <table class="data-table">
    ...
  </table>
</div>
```

### CSS
```css
.table-scroll-wrapper {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  position: relative;
}

.data-table {
  width: max-content;
  min-width: 100%;
  table-layout: fixed;
}
```

### Kết quả
- Resize column → table rộng
- Scroll ngang xuất hiện
- Không tràn viewport

---

## 4. Giải pháp B (Khóa cứng width table)

### JS
```js
const totalWidth = Array.from(headers)
  .reduce((sum, th) => sum + th.offsetWidth, 0);

table.style.width = `${totalWidth}px`;
```

### Nhược điểm
- UX kém hơn
- Không linh hoạt khi resize nhiều cột

---

## 5. Giải pháp C (Hybrid – chuyên nghiệp nhất)

### JS
```js
function updateTableWidth(headers, table) {
  let total = 0;
  headers.forEach(th => total += th.offsetWidth);
  table.style.width = `${total}px`;
}
```

Gọi trong:
- `mousemove`
- `mouseup`

### Ưu điểm
- Resize mượt
- Scroll chuẩn
- Hành vi giống Excel

---

## 6. CSS cần chỉnh trong layout

### Tránh
```css
.dashboard-container {
  max-width: 95%;
}
```

### Nên dùng
```css
.dashboard-container {
  max-width: 100%;
  overflow-x: hidden;
}
```

---

## 7. Checklist nhanh

- [ ] Table nằm trong scroll container
- [ ] `overflow-x: auto`
- [ ] Table dùng `width: max-content`
- [ ] Không resize trực tiếp phá viewport

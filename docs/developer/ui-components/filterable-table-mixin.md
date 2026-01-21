# Hướng dẫn sử dụng FilterableTableMixin

`FilterableTableMixin` cung cấp một công cụ tổng quát để lọc dữ liệu phía client. Thay vì phải viết các vòng lặp và câu lệnh `if` tùy chỉnh cho từng bảng, bạn chỉ cần định nghĩa một **Đối tượng Cấu hình (Configuration Object)** ánh xạ các đầu vào bộ lọc tới các trường dữ liệu.

## Tính năng
- **Khai báo (Declarative)**: Định nghĩa *cái gì* cần lọc, thay vì *cách* lọc.
- **Các loại hỗ trợ**: `text` (tìm kiếm mờ), `exact` (so sánh chính xác - dùng cho dropdown), `array_includes` (kiểm tra mảng - dùng cho tag/nhóm), `date` (tìm kiếm theo ngày tháng).
- **Tự động xử lý**: Tự động xử lý các giá trị null, chuỗi rỗng và không phân biệt chữ hoa chữ thường.

## Cài đặt

```javascript
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
    mixins: [FilterableTableMixin],
    // ...
}
```

## Cách sử dụng cơ bản

1.  **Định nghĩa trạng thái bộ lọc**: Tạo một đối tượng trong `data()` để lưu trữ các giá trị nhập vào.
2.  **Liên kết đầu vào (Bind Inputs)**: Sử dụng `v-model` trong template của bạn.
3.  **Tính toán kết quả**: Gọi hàm `this.filterArray(items, filters, config)` trong một computed property.

## Ví dụ thực tế: Thêm bộ lọc "Ngày tháng" vào Dashboard

**Tình huống**: Bạn có một bảng danh sách Hồ sơ vay và muốn lọc theo ngày tạo (`created_at`).

### Bước 1: Thêm Input vào Template
Thêm một input loại date liên kết với `filters.createdDate`.

```html
<div class="filter-bar">
    <!-- Tìm kiếm hiện có -->
    <div class="filter-group">
        <label>Tìm kiếm</label>
        <input v-model="filters.search" class="filter-control" placeholder="Tìm kiếm...">
    </div>
    
    <!-- MỚI: Bộ lọc Ngày -->
    <div class="filter-group">
        <label>Ngày tạo</label>
        <input type="date" v-model="filters.createdDate" class="filter-control">
    </div>
</div>
```

### Bước 2: Cập nhật trạng thái dữ liệu (Data State)
Khởi tạo biến `createdDate`.

```javascript
data() {
    return {
        // ...
        filters: {
            search: '',
            status: null,
            createdDate: '' // <--- MỚI
        }
    }
}
```

### Bước 3: Cấu hình Logic lọc
Trong computed property của bạn, thêm ánh xạ vào đối tượng cấu hình.

```javascript
computed: {
    sortedProfiles() {
        // 1. Lọc
        const filtered = this.filterArray(this.profiles, this.filters, {
            // Tìm kiếm hiện có
            search: { type: 'text', fields: ['name', 'created_by_user_name'] },
            
            // Trạng thái hiện có
            status: { type: 'exact' },
            
            // MỚI: Bộ lọc Ngày
            // 'type: date' trích xuất YYYY-MM-DD từ trường dữ liệu và so sánh với chuỗi nhập vào.
            createdDate: { type: 'date', field: 'created_at' }
        });

        // 2. Sắp xếp (sử dụng SortableTableMixin)
        return this.sortArray(filtered);
    }
}
```

## Tài liệu tham khảo cấu hình (Configuration Reference)

Các key trong đối tượng `config` phải khớp với các key trong đối tượng `filters` của bạn.

| Loại (Type) | Cách dùng | Ví dụ |
| :--- | :--- | :--- |
| `text` | Khớp một phần, không phân biệt hoa thường. | `{ type: 'text', fields: ['name', 'email'] }` |
| `exact` | Kiểm tra bằng nhau tuyệt đối (tốt cho ID, Trạng thái). | `{ type: 'exact', field: 'status_code' }` |
| `array_includes` | Kiểm tra xem *mảng của phần tử dữ liệu* có chứa giá trị lọc không. | `{ type: 'array_includes', field: 'allowed_roles' }` |
| `date` | Khớp chuỗi YYYY-MM-DD với đối tượng Date hoặc chuỗi ISO. | `{ type: 'date', field: 'created_at' }` |

### Các tùy chọn chung
- `field` (String): Tên trường trong hàng dữ liệu cần kiểm tra. Mặc định là key của bộ lọc nếu bỏ qua.
- `fields` (Array): Chỉ dành cho loại `text`. Danh sách các trường cần kiểm tra (logic HOẶC).

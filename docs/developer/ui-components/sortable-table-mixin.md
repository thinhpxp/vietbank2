# Hướng dẫn sử dụng SortableTableMixin

`SortableTableMixin` cung cấp một cách tiêu chuẩn để triển khai việc sắp xếp dữ liệu phía client cho các bảng trong ứng dụng Vue. Nó quản lý trạng thái sắp xếp (`sortBy`, `sortDesc`), cung cấp các phương thức hỗ trợ để đảm bảo tính nhất quán của giao diện (UI), và cung cấp logic sắp xếp mảng mạnh mẽ.

## Tính năng

- **Quản lý trạng thái**: Tự động xử lý `sortBy` (cột hiện tại) và `sortDesc` (hướng sắp xếp).
- **Nhất quán giao diện**: Tích hợp với các CSS class tiêu chuẩn (`.ui-sortable`).
- **Sắp xếp mạnh mẽ**:
  - Xử lý các giá trị `null`/`undefined` một cách an toàn.
  - Sắp xếp chuỗi không phân biệt hoa thường.
  - Ánh xạ cột tùy chỉnh (ví dụ: sắp xếp theo ID nhưng sử dụng Tên để so sánh).
- **Tái sử dụng**: Dễ dàng áp dụng cho bất kỳ component nào có bảng.

## Cài đặt

Import và đăng ký mixin trong component Vue của bạn:

```javascript
import { SortableTableMixin } from '@/mixins/SortableTableMixin';

export default {
    mixins: [SortableTableMixin],
    // ...
}
```

## Cách sử dụng

### 1. Thiết lập Template (Tiêu đề bảng)

Sử dụng `toggleSort` cho sự kiện click và `:class="getSortableClass(...)"` để định dạng style. Sử dụng `getSortIcon(...)` để hiển thị mũi tên sắp xếp.

```html
<thead>
  <tr>
    <th 
        @click="toggleSort('id')" 
        :class="getSortableClass('id')"
    >
        ID {{ getSortIcon('id') }}
    </th>
    
    <th 
        @click="toggleSort('name')" 
        :class="getSortableClass('name')"
    >
        Tên {{ getSortIcon('name') }}
    </th>
  </tr>
</thead>
```

### 2. Hiển thị dữ liệu đã sắp xếp

Sử dụng phương thức `sortArray` bên trong một computed property để hiển thị danh sách.

```javascript
computed: {
    sortedItems() {
        // 'this.items' là mảng dữ liệu thô của bạn
        return this.sortArray(this.items);
    }
}
```

Sau đó trong template của bạn:

```html
<tr v-for="item in sortedItems" :key="item.id">
    <!-- ... -->
</tr>
```

## Tài liệu tham khảo API

### Thuộc tính dữ liệu (Trạng thái)

| Thuộc tính | Kiểu | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `sortBy` | String | `''` | Tên cột hiện đang được sắp xếp. |
| `sortDesc` | Boolean | `false` | Hướng sắp xếp (`true` = Giảm dần, `false` = Tăng dần). |

### Các phương thức (Methods)

#### `toggleSort(column)`
Chuyển đổi trạng thái sắp xếp cho một cột nhất định.
- Nếu click vào *cùng* một cột: Đảo ngược thứ tự (`sortDesc` = `!sortDesc`).
- Nếu click vào một cột *mới*: Đặt `sortBy` thành cột mới và đặt lại `sortDesc` về `false`.

#### `getSortIcon(column)`
Trả về ký hiệu trực quan (▲ hoặc ▼) nếu cột đó đang được sắp xếp. Trả về chuỗi rỗng nếu không.

#### `getSortableClass()`
Trả về chuỗi CSS class tiêu chuẩn `'ui-sortable'`. Lớp này áp dụng:
- `cursor: pointer`
- `user-select: none`
- Hiệu ứng hover (thay đổi nền/màu sắc) được định nghĩa trong `common-ui.css`.

#### `sortArray(items, mapping)`
Trả về một **mảng mới đã được sắp xếp** (không thay đổi mảng gốc).

- **items** *(Array)*: Danh sách các đối tượng cần sắp xếp.
- **mapping** *(Object, tùy chọn)*: Bản đồ key-value cho logic sắp xếp tùy chỉnh.

**Ví dụ về Mapping:**
Nếu bạn có cột `group_id` nhưng muốn sắp xếp theo bảng chữ cái theo `group_name`:

```javascript
return this.sortArray(this.users, {
    'group_id': 'group_name',  // key trong sortBy : key thực tế để đọc từ đối tượng
    'status': 'status_label'
});
```

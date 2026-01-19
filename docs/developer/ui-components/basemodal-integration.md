# Hướng dẫn Tích hợp BaseModal

## Tổng quan

`BaseModal.vue` là một component modal có thể tái sử dụng và thay đổi kích thước, được thiết kế để cung cấp giao diện nhất quán trong toàn bộ ứng dụng. Component hỗ trợ teleportation đến body, logic resize tích hợp sẵn, và nội dung linh hoạt thông qua slots.

> **Đối tượng**: Lập trình viên Frontend cần tích hợp modal vào các component Vue.

## Vị trí File

```
frontend/src/components/BaseModal.vue
```

## Cách sử dụng Cơ bản

### 1. Import và Đăng ký

```javascript
import BaseModal from '@/components/BaseModal.vue';

export default {
  components: { BaseModal },
  // ...
}
```

### 2. Cấu trúc Template

```vue
<BaseModal 
    :isOpen="isModalOpen" 
    title="Tiêu đề Modal" 
    @close="isModalOpen = false"
>
    <!-- Slot mặc định: Nội dung Modal -->
    <p>Đây là nội dung chính của modal.</p>

    <!-- Slot Footer (Tùy chọn) -->
    <template #footer>
        <button @click="isModalOpen = false">Đóng</button>
        <button @click="handleAction">Thực hiện</button>
    </template>

    <!-- Slot Header Actions (Tùy chọn) -->
    <template #header-actions>
        <button class="btn-icon">⭐</button>
    </template>
</BaseModal>
```

## Props (Thuộc tính)

| Prop | Kiểu | Mặc định | Mô tả |
|------|------|---------|-------|
| `isOpen` | Boolean | **Bắt buộc** | Điều khiển hiển thị modal. |
| `title` | String | 'Modal' | Text hiển thị trong header. |
| `initialWidth` | Number/String | 650 | Chiều rộng khởi tạo (pixels). |
| `initialHeight` | Number/String | null | Chiều cao khởi tạo. Nếu null, tự động điều chỉnh theo nội dung. |
| `isResizable` | Boolean | true | Bật/tắt chức năng resize. |
| `minWidth` | Number | 400 | Chiều rộng tối thiểu khi resize. |
| `minHeight` | Number | 200 | Chiều cao tối thiểu khi resize. |
| `closeOnOverlay` | Boolean | false | Nếu true, click vào overlay sẽ đóng modal. |

## Slots (Vùng nội dung)

- **default**: Nội dung chính của modal. Vùng này có thể cuộn (scrollable).
- **header**: Thay thế toàn bộ nội dung header (thay thế title, nhưng giữ lại actions và nút đóng trừ khi tùy chỉnh).
- **header-actions**: Vùng bên trái nút đóng [x] để thêm icon hoặc button tùy chỉnh.
- **footer**: Vùng cố định ở phía dưới cho các nút hành động (Hủy, Lưu, v.v.).

## Ví dụ Sử dụng

### Ví dụ 1: Modal Đơn giản

```vue
<template>
  <div>
    <button @click="showModal = true">Mở Modal</button>
    
    <BaseModal 
      :isOpen="showModal" 
      title="Xác nhận"
      @close="showModal = false"
    >
      <p>Bạn có chắc chắn muốn thực hiện hành động này?</p>
      
      <template #footer>
        <button class="btn-action btn-secondary" @click="showModal = false">
          Hủy
        </button>
        <button class="btn-action btn-primary" @click="handleConfirm">
          Xác nhận
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import BaseModal from '@/components/BaseModal.vue';

export default {
  components: { BaseModal },
  data() {
    return {
      showModal: false
    };
  },
  methods: {
    handleConfirm() {
      // Xử lý logic
      this.showModal = false;
    }
  }
};
</script>
```

### Ví dụ 2: Modal với Chiều cao Cố định

```vue
<BaseModal 
  :isOpen="isOpen" 
  title="Danh sách Người dùng"
  :initialHeight="500"
  @close="isOpen = false"
>
  <div class="user-list">
    <!-- Nội dung dài sẽ tự động cuộn -->
    <div v-for="user in users" :key="user.id">
      {{ user.name }}
    </div>
  </div>
  
  <template #footer>
    <button class="btn-action btn-primary">Thêm người dùng</button>
  </template>
</BaseModal>
```

### Ví dụ 3: Modal Không thể Resize

```vue
<BaseModal 
  :isOpen="isOpen" 
  title="Thông báo"
  :isResizable="false"
  :initialWidth="400"
  @close="isOpen = false"
>
  <p>Đây là một thông báo quan trọng.</p>
  
  <template #footer>
    <button class="btn-action btn-primary" @click="isOpen = false">
      Đã hiểu
    </button>
  </template>
</BaseModal>
```

### Ví dụ 4: Modal với Header Actions

```vue
<BaseModal 
  :isOpen="isOpen" 
  title="Chỉnh sửa Hồ sơ"
  @close="isOpen = false"
>
  <form>
    <!-- Form fields -->
  </form>
  
  <template #header-actions>
    <button class="btn-icon" @click="toggleFavorite" title="Yêu thích">
      <SvgIcon name="star" size="sm" />
    </button>
    <button class="btn-icon" @click="openHelp" title="Trợ giúp">
      <SvgIcon name="info" size="sm" />
    </button>
  </template>
  
  <template #footer>
    <button class="btn-action btn-secondary" @click="isOpen = false">
      Hủy
    </button>
    <button class="btn-action btn-success" @click="saveProfile">
      <SvgIcon name="save" size="sm" /> Lưu
    </button>
  </template>
</BaseModal>
```

## Thực hành Tốt nhất

### ✅ Nên làm

1. **Chiều cao Cố định cho Nội dung Dài**
   ```vue
   <!-- Tốt: Đặt chiều cao cố định cho danh sách dài -->
   <BaseModal :initialHeight="600" title="Danh sách">
     <!-- Nội dung dài -->
   </BaseModal>
   ```

2. **Sử dụng Footer cho Hành động**
   ```vue
   <!-- Tốt: Đặt nút hành động trong footer -->
   <template #footer>
     <button class="btn-action btn-secondary">Hủy</button>
     <button class="btn-action btn-primary">Lưu</button>
   </template>
   ```

3. **Đặt tên Class Chuẩn**
   ```vue
   <!-- Tốt: Sử dụng class từ design system -->
   <button class="btn-action btn-primary">Lưu</button>
   <button class="btn-action btn-secondary">Hủy</button>
   ```

### ❌ Không nên làm

1. **Không đặt chiều cao quá nhỏ**
   ```vue
   <!-- Không tốt: Chiều cao quá nhỏ -->
   <BaseModal :initialHeight="100">
     <!-- Nội dung sẽ bị cắt -->
   </BaseModal>
   ```

2. **Không đặt nút hành động trong body**
   ```vue
   <!-- Không tốt: Nút nằm trong body, không cố định -->
   <BaseModal>
     <p>Nội dung</p>
     <button>Lưu</button> <!-- Sẽ cuộn theo nội dung -->
   </BaseModal>
   ```

3. **Không dùng inline styles**
   ```vue
   <!-- Không tốt: Dùng inline style -->
   <BaseModal style="width: 800px;">
     <!-- Dùng prop initialWidth thay thế -->
   </BaseModal>
   ```

## Tính năng Nâng cao

### Tự động Cuộn (Auto-scroll)

Nội dung modal tự động cuộn nếu vượt quá chiều cao:

```vue
<BaseModal :initialHeight="400">
  <div style="height: 1000px;">
    <!-- Nội dung dài sẽ tự động cuộn -->
  </div>
</BaseModal>
```

### Resize Động

Người dùng có thể kéo góc dưới bên phải để thay đổi kích thước:

```vue
<BaseModal 
  :isResizable="true"
  :minWidth="500"
  :minHeight="300"
>
  <!-- Nội dung -->
</BaseModal>
```

### Đóng khi Click Overlay

```vue
<BaseModal 
  :closeOnOverlay="true"
  @close="handleClose"
>
  <!-- Click vào vùng tối phía sau sẽ đóng modal -->
</BaseModal>
```

## Styling

### CSS Classes Có sẵn

Modal sử dụng các class sau (có thể override trong component cha):

```css
.modal-overlay     /* Lớp phủ tối phía sau */
.modal-container   /* Container chính của modal */
.modal-header      /* Header chứa title và nút đóng */
.modal-body        /* Nội dung chính (scrollable) */
.modal-footer      /* Footer chứa nút hành động */
.resize-handle     /* Nút kéo để resize */
```

### Tùy chỉnh Styles

```vue
<BaseModal class="custom-modal">
  <!-- Nội dung -->
</BaseModal>

<style scoped>
.custom-modal .modal-body {
  background: #f5f5f5;
  padding: 20px;
}

.custom-modal .modal-footer {
  justify-content: space-between;
}
</style>
```

## Xử lý Sự cố

### Modal không hiển thị

**Nguyên nhân**: Prop `isOpen` không được set đúng

**Giải pháp**:
```javascript
data() {
  return {
    isModalOpen: false  // Đảm bảo có biến này
  };
}
```

### Nội dung bị cắt

**Nguyên nhân**: `initialHeight` quá nhỏ hoặc `minHeight` quá nhỏ

**Giải pháp**:
```vue
<BaseModal 
  :initialHeight="500"
  :minHeight="300"
>
```

### Không resize được

**Nguyên nhân**: `isResizable` bị set thành `false`

**Giải pháp**:
```vue
<BaseModal :isResizable="true">
```

## Tích hợp với Design System

BaseModal tự động kế thừa các style từ design system:

```vue
<BaseModal>
  <template #footer>
    <!-- Sử dụng button classes từ design system -->
    <button class="btn-action btn-secondary">Hủy</button>
    <button class="btn-action btn-primary">
      <SvgIcon name="save" size="sm" /> Lưu
    </button>
  </template>
</BaseModal>
```

## Tài nguyên Liên quan

- **[Design System Guidelines](./design-system.md)**: Hướng dẫn sử dụng button và form classes
- **[SVG Icon System](./svg-icon-system.md)**: Cách sử dụng icon trong modal
- **Component Source**: `frontend/src/components/BaseModal.vue`

---

**Phiên bản tài liệu**: 1.0  
**Cập nhật lần cuối**: 19/01/2026  
**Người bảo trì**: Vietbank Development Team

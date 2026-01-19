# Kiến trúc Frontend

## Tổng quan

Frontend của Vietbank Contract App được xây dựng với **Vue 3** sử dụng Composition API và Vue Router cho điều hướng. Ứng dụng tuân theo kiến trúc dựa trên component với quản lý state tập trung và hệ thống thiết kế thống nhất.

## Công nghệ Sử dụng

- **Framework**: Vue 3 (Composition API)
- **Router**: Vue Router 4
- **Quản lý State**: Vuex 4 (module auth)
- **HTTP Client**: Axios
- **Build Tool**: Vue CLI / Webpack
- **CSS**: SCSS + CSS (modular)
- **Icons**: Hệ thống SVG component tùy chỉnh

## Cấu trúc Dự án

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── assets/
│   │   ├── tokens.scss          # Design tokens
│   │   ├── common-ui.css        # Component UI chung
│   │   ├── admin.css            # Style admin
│   │   └── icons.css            # Tiện ích SVG icon
│   ├── components/
│   │   ├── common/
│   │   │   └── SvgIcon.vue      # Component icon SVG toàn cục
│   │   ├── AppToast.vue         # Thông báo toast
│   │   └── ConfirmModal.vue     # Hộp thoại xác nhận
│   ├── views/
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── ProfileView.vue      # Quản lý tài khoản
│   │   ├── DashboardView.vue
│   │   ├── LoanProfileForm.vue
│   │   └── admin/               # Các trang admin
│   ├── router/
│   │   └── index.js             # Định nghĩa route
│   ├── store/
│   │   └── auth.js              # State xác thực
│   ├── utils/
│   │   ├── toast.js             # Plugin toast
│   │   └── resizable-table.js   # Tiện ích resize table
│   ├── App.vue                  # Component gốc
│   └── main.js                  # Entry point
├── package.json
└── vue.config.js
```

## Khái niệm Cốt lõi

### 1. Kiến trúc Component

#### Component Toàn cục
Đăng ký trong `main.js`, có sẵn ở mọi nơi:
- `SvgIcon`: Hệ thống icon SVG

#### Component Trang (Views)
Nằm trong `src/views/`, ánh xạ tới routes:
- **Public**: Login, Register
- **Authenticated**: Dashboard, Profile, LoanProfileForm
- **Admin**: AdminLayout và các route con

#### Component Tái sử dụng
Nằm trong `src/components/`:
- `AppToast`: Hệ thống thông báo toàn cục
- `ConfirmModal`: Hộp thoại xác nhận
- `SvgIcon`: Render icon

### 2. Routing

**File**: `src/router/index.js`

#### Cấu trúc Route
```javascript
const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { 
    path: '/', 
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  { 
    path: '/profile', 
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: 'groups', component: AdminGroups },
      // ...
    ]
  }
];
```

#### Navigation Guards
```javascript
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!auth.state.token;
  const isAdmin = auth.state.user?.is_staff || auth.state.user?.is_superuser;

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login');
  }

  if (to.meta.requiresAdmin && !isAdmin) {
    return next('/');
  }

  next();
});
```

### 3. Quản lý State

**File**: `src/store/auth.js`

#### Cấu trúc Auth Store
```javascript
export default {
  state: {
    token: null,
    user: null,
    permissions: []
  },
  
  mutations: {
    setAuth(state, { token, user }) { ... },
    clearAuth(state) { ... }
  },
  
  actions: {
    async login({ commit }, credentials) { ... },
    logout({ commit }) { ... },
    initialize({ commit }) { ... }
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    isSuperuser: state => state.user?.is_superuser,
    isStaff: state => state.user?.is_staff,
    displayName: state => state.user?.profile?.full_name || state.user?.username
  }
};
```

### 4. Tích hợp API

**HTTP Client**: Axios với interceptors

#### Cấu hình
```javascript
// Axios instance với base URL
axios.defaults.baseURL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';

// Request interceptor (thêm auth token)
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Response interceptor (xử lý 401)
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      auth.actions.logout();
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

#### Mẫu API Call
```javascript
// GET request
async fetchUsers() {
  const response = await axios.get('/users/');
  this.users = response.data;
}

// POST request
async createUser(userData) {
  await axios.post('/users/', userData);
}

// PATCH request
async updateProfile(profileData) {
  await axios.patch('/me/', profileData);
}

// DELETE request
async deleteUser(userId) {
  await axios.delete(`/users/${userId}/`);
}
```

## Tính năng Chính

### 1. Luồng Xác thực

```
Người dùng truy cập app
    ↓
Có token? → Không → Chuyển đến /login
    ↓ Có
Tải dữ liệu user
    ↓
Token hợp lệ? → Không → Chuyển đến /login
    ↓ Có
Hiển thị nội dung được bảo vệ
```

### 2. Kiến trúc Admin Panel

**Mẫu split-pane** cho danh sách + editor:
```vue
<div class="split-view">
  <!-- Trái: Danh sách -->
  <div class="pane pane-left" :style="{ width: paneWidth + '%' }">
    <div class="pane-header admin-row">
      <input class="admin-form-control flex-1" />
      <button class="btn-action btn-primary">Thêm</button>
    </div>
    <div class="table-container scrollable">
      <table class="data-table">...</table>
    </div>
  </div>
  
  <!-- Phải: Editor -->
  <div class="pane pane-right">
    <div class="editor-container">
      <!-- Form chỉnh sửa -->
    </div>
  </div>
</div>
```

### 3. Validation Form

**Mẫu**: Validation phía client trước khi gọi API
```javascript
methods: {
  validateForm() {
    if (!this.form.username) {
      this.$toast.error('Username là bắt buộc');
      return false;
    }
    if (this.form.password.length < 8) {
      this.$toast.error('Mật khẩu phải có ít nhất 8 ký tự');
      return false;
    }
    return true;
  },
  
  async submitForm() {
    if (!this.validateForm()) return;
    
    try {
      await axios.post('/users/', this.form);
      this.$toast.success('Tạo user thành công');
    } catch (error) {
      this.$toast.error(error.response?.data?.message || 'Có lỗi xảy ra');
    }
  }
}
```

## Thực hành Tốt nhất

### 1. Tổ chức Component

```vue
<template>
  <!-- Template -->
</template>

<script>
// 1. Imports
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

// 2. Định nghĩa component
export default {
  name: 'ComponentName',
  props: { ... },
  data() { return { ... }; },
  computed: { ... },
  mounted() { ... },
  methods: { ... }
};
</script>

<style scoped>
/* Style riêng component */
</style>
```

### 2. Xử lý Lỗi

```javascript
async fetchData() {
  try {
    const response = await axios.get('/api/endpoint/');
    this.data = response.data;
  } catch (error) {
    console.error('Lỗi tải dữ liệu:', error);
    this.$toast.error('Không thể tải dữ liệu');
  }
}
```

### 3. Loading States

```vue
<template>
  <div>
    <div v-if="loading">Đang tải...</div>
    <div v-else-if="error">Lỗi: {{ error }}</div>
    <div v-else>
      <!-- Nội dung -->
    </div>
  </div>
</template>
```

## Cân nhắc Hiệu suất

### 1. Lazy Loading Routes
```javascript
const routes = [
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue')
  }
];
```

### 2. Debouncing Search
```javascript
import { debounce } from 'lodash';

methods: {
  handleSearch: debounce(function(query) {
    this.fetchResults(query);
  }, 300)
}
```

## Build & Deployment

### Build cho Production
```bash
npm run build
```

### Biến Môi trường
```env
VUE_APP_API_URL=https://api.vietbank.com
VUE_APP_ENV=production
```

## Tài nguyên

- **Vue 3 Docs**: https://vuejs.org/
- **Vue Router**: https://router.vuejs.org/
- **Design System**: Xem `design-system.md`
- **Icon System**: Xem `svg-icon-system.md`

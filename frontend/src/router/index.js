// Chức năng: Định nghĩa các tuyến đường cho ứng dụng Vue.js sử dụng Vue Router
// Mục đích: Quản lý điều hướng giữa các trang Dashboard và LoanProfileForm
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';     // Chúng ta sẽ tạo file này ở bước 2
import LoanProfileForm from '../views/LoanProfileForm.vue';

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/create',
    name: 'CreateProfile',
    component: LoanProfileForm
  },
  {
    path: '/edit/:id', // :id là tham số động (VD: /edit/1)
    name: 'EditProfile',
    component: LoanProfileForm,
    props: true // Cho phép truyền id vào component như một prop
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
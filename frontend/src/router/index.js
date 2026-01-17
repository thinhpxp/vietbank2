// Chức năng: Định nghĩa các tuyến đường cho ứng dụng Vue.js sử dụng Vue Router
// Mục đích: Quản lý điều hướng giữa các trang Dashboard và LoanProfileForm
import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';     // Chúng ta sẽ tạo file này ở bước 2
import LoanProfileForm from '../views/LoanProfileForm.vue';
// Import các view Admin (sẽ tạo sau)
import AdminLayout from '../views/admin/AdminLayout.vue';
import AdminGroups from '../views/admin/AdminGroups.vue';
import AdminFields from '../views/admin/AdminFields.vue';
import AdminTemplates from '../views/admin/AdminTemplates.vue';
import AdminAccessManagement from '../views/admin/AdminAccessManagement.vue';
import AdminRoles from '../views/admin/AdminRoles.vue';
import AdminForms from '../views/admin/AdminForms.vue';
import AdminObjectTypes from '../views/admin/AdminObjectTypes.vue';
import MasterData from '../views/admin/MasterData.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import auth from '@/store/auth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/create',
    name: 'CreateProfile',
    component: LoanProfileForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit/:id',
    name: 'EditProfile',
    component: LoanProfileForm,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/master-data',
    name: 'MasterData',
    component: () => import('@/views/admin/MasterData.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: 'groups', component: AdminGroups },
      { path: 'fields', component: AdminFields },
      { path: 'templates', component: AdminTemplates },
      { path: 'users', component: AdminAccessManagement },
      { path: 'roles', component: AdminRoles },
      { path: 'forms', component: AdminForms },
      { path: 'object-types', component: AdminObjectTypes },
      { path: 'master-data', component: MasterData },
      { path: '', redirect: '/admin/groups' }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Global Navigation Guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = auth.state.isAuthenticated;
  const isAdmin = auth.isAdmin.value;

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Nếu chưa đăng nhập mà vào trang yêu cầu auth -> Chuyển về Login
    next('/login');
  } else if (to.meta.requiresAdmin && !isAdmin) {
    // Nếu không phải admin mà vào trang Admin -> Chuyển về Dashboard
    next('/');
  } else if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    // Nếu đã đăng nhập mà cố vào trang Login/Register -> Chuyền về Dashboard
    next('/');
  } else {
    next();
  }
});

export default router;
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
import AdminUsers from '../views/admin/AdminUsers.vue';
import AdminRoles from '../views/admin/AdminRoles.vue';
import AdminForms from '../views/admin/AdminForms.vue';
import AdminObjectTypes from '../views/admin/AdminObjectTypes.vue'; // <-- MỚI
import MasterData from '../views/admin/MasterData.vue';

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView
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
  },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      { path: 'groups', component: AdminGroups },
      { path: 'fields', component: AdminFields },
      { path: 'templates', component: AdminTemplates },
      { path: 'users', component: AdminUsers },
      { path: 'roles', component: AdminRoles },
      { path: 'forms', component: AdminForms },
      { path: 'object-types', component: AdminObjectTypes }, // <-- MỚI
      { path: 'master-data', component: MasterData },
      { path: '', redirect: '/admin/groups' } // Mặc định vào trang Groups
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
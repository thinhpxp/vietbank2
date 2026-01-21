<template>
  <div class="admin-page">
    <h2>Quản lý Vai trò (Roles)</h2>
    <div class="admin-panel">
      <h4>Thêm vai trò mới</h4>
      <div class="admin-row">
        <input v-model="newRole.name" placeholder="Tên vai trò mới (VD: Người Thừa kế)" class="admin-input">
        <input v-model="newRole.slug" placeholder="Mã định danh (Slug - VD: nguoi_thua_ke)" class="admin-input">
        <input v-model="newRole.description" placeholder="Mô tả (Tùy chọn)" class="admin-input">
        <input v-model="newRole.relation_type" placeholder="Quan hệ (VD: OWNER)" class="admin-input">
        <button @click="addRole" class="btn-action btn-create">Thêm Vai trò</button>
      </div>
    </div>

    <div class="ui-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên Vai trò</th>
            <th>Mã (Slug)</th>
            <th>Mô tả</th>
            <th>Quan hệ Tự động</th>
            <th>Hệ thống</th>
            <th>Hành động</th>
          </tr>
        </thead>

        <tbody class="tbody">
          <tr v-for="role in roles" :key="role.id">
            <td>{{ role.id }}</td>
            <td>
              <input v-if="editingId === role.id" v-model="role.name">
              <span v-else>{{ role.name }}</span>
            </td>
            <td>
              <input v-if="editingId === role.id" v-model="role.slug">
              <span v-else>{{ role.slug || '---' }}</span>
            </td>
            <td>
              <input v-if="editingId === role.id" v-model="role.description" style="width: 100%" class="admin-input">
              <span v-else>{{ role.description }}</span>
            </td>
            <td>
              <input v-if="editingId === role.id" v-model="role.relation_type" placeholder="OWNER..."
                class="admin-input">
              <span v-else>{{ role.relation_type || '---' }}</span>
            </td>
            <td style="text-align: center;">
              <span v-if="role.is_system" class="badge badge-system">System</span>
              <span v-else class="badge badge-user">User</span>
            </td>
            <td>
              <div class="flex gap-2">
                <button v-if="editingId === role.id" @click="updateRole(role)" class="btn-action btn-save">Lưu</button>
                <button v-else @click="editingId = role.id" class="btn-action btn-edit">Sửa</button>

                <button v-if="!role.is_system" @click="deleteRole(role.id)" class="btn-action btn-delete">Xóa</button>
                <span v-else title="Role hệ thống không thể xóa" class="text-gray-400 px-2 cursor-not-allowed">🔒</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa vai trò '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { makeTableResizable } from '../../utils/resizable-table';
import { errorHandlingMixin } from '../../utils/errorHandler';

export default {
  name: 'AdminRoles',
  components: { ConfirmModal },
  mixins: [errorHandlingMixin],
  data() {
    return {
      roles: [],
      newRole: { name: '', slug: '', description: '', relation_type: '' },
      editingId: null,
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  mounted() {
    this.fetchRoles();
    this.initResizable();
  },
  methods: {
    async fetchRoles() {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/roles/');
        this.roles = res.data;
        this.$nextTick(() => this.initResizable());
      } catch (e) {
        console.error("Lỗi tải roles:", e);
      }
    },
    initResizable() {
      const table = this.$el.querySelector('.data-table');
      if (table) {
        makeTableResizable(table, 'admin-roles');
      }
    },
    async addRole() {
      if (!this.newRole.name) {
        this.showWarning('Vui lòng nhập tên vai trò', 'Thiếu thông tin');
        return;
      }
      try {
        await axios.post('http://127.0.0.1:8000/api/roles/', this.newRole);
        this.newRole.name = '';
        this.newRole.slug = '';
        this.newRole.description = '';
        this.fetchRoles();
      } catch (e) {
        this.showError(e, 'Lỗi thêm vai trò');
      }
    },
    deleteRole(id) {
      const role = this.roles.find(r => r.id === id);
      this.deleteTargetId = id;
      this.deleteTargetName = role ? role.name : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        try {
          await axios.delete(`http://127.0.0.1:8000/api/roles/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchRoles();
        } catch (e) {
          this.showError(e, 'Lỗi xóa vai trò');
        }
      }
    },
    async updateRole(role) {
      try {
        await axios.put(`http://127.0.0.1:8000/api/roles/${role.id}/`, role);
        this.editingId = null;
      } catch (e) {
        this.showError(e, 'Lỗi cập nhật vai trò');
      }
    }
  }
}
</script>

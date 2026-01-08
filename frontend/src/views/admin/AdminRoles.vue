<template>
  <div class="admin-page">
    <h2>Quản lý Vai trò (Roles)</h2>
    <div class="actions">
      <input v-model="newRole.name" placeholder="Tên vai trò mới (VD: Người Thừa kế)" style="flex: 1">
      <input v-model="newRole.slug" placeholder="Mã định danh (Slug - VD: nguoi_thua_ke)" style="flex: 1">
      <input v-model="newRole.description" placeholder="Mô tả (Tùy chọn)" style="flex: 2">
      <button @click="addRole" class="btn-action btn-create">Thêm Vai trò</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Tên Vai trò</th>
          <th>Mã (Slug)</th>
          <th>Mô tả</th>
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
            <input v-if="editingId === role.id" v-model="role.description" style="width: 100%">
            <span v-else>{{ role.description }}</span>
          </td>
          <td>
            <div class="action-group">
              <button v-if="editingId === role.id" @click="updateRole(role)" class="btn-action btn-save">Lưu</button>
              <button v-else @click="editingId = role.id" class="btn-action btn-edit">Sửa</button>
              <button @click="deleteRole(role.id)" class="btn-action btn-delete">Xóa</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa vai trò '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';

export default {
  components: { ConfirmModal },
  data() {
    return {
      roles: [],
      newRole: { name: '', slug: '', description: '' },
      editingId: null,
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  mounted() { this.fetchRoles(); },
  methods: {
    async fetchRoles() {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/roles/');
        this.roles = res.data;
      } catch (e) {
        console.error("Lỗi tải roles:", e);
      }
    },
    async addRole() {
      if (!this.newRole.name) return alert('Vui lòng nhập tên vai trò');
      try {
        await axios.post('http://127.0.0.1:8000/api/roles/', this.newRole);
        this.newRole.name = '';
        this.newRole.slug = '';
        this.newRole.description = '';
        this.fetchRoles();
      } catch (e) {
        alert('Lỗi thêm vai trò: ' + e.response?.data?.message || e.message);
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
          alert('Lỗi xóa vai trò');
        }
      }
    },
    async updateRole(role) {
      try {
        await axios.put(`http://127.0.0.1:8000/api/roles/${role.id}/`, role);
        this.editingId = null;
      } catch (e) {
        alert('Lỗi cập nhật vai trò');
      }
    }
  }
}
</script>

<style scoped>
.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.action-group {
  display: flex;
  gap: 5px;
}
</style>

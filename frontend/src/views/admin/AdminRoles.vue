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

    <div class="filter-bar mb-4">
      <div class="filter-group">
        <label>Tìm kiếm:</label>
        <input v-model="filters.search" placeholder="Tìm theo tên hoặc mã..." class="admin-form-control"
          style="width: 300px">
      </div>
    </div>

    <div class="data-table-vxe">
      <vxe-table border round :data="filteredRoles" :row-config="{ isHover: true }" :column-config="{ resizable: true }"
        :sort-config="{ trigger: 'cell' }">
        <vxe-column field="id" title="ID" width="60" sortable></vxe-column>
        <vxe-column field="name" title="Tên Vai trò" min-width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.name" class="vxe-input-minimal">
            <span v-else>{{ row.name }}</span>
          </template>
        </vxe-column>
        <vxe-column field="slug" title="Mã (Slug)" width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.slug" class="vxe-input-minimal">
            <span v-else>{{ row.slug || '---' }}</span>
          </template>
        </vxe-column>
        <vxe-column field="description" title="Mô tả" min-width="200">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.description" class="vxe-input-minimal">
            <span v-else>{{ row.description }}</span>
          </template>
        </vxe-column>
        <vxe-column field="relation_type" title="Quan hệ Tự động" width="150">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.relation_type" class="vxe-input-minimal"
              placeholder="OWNER...">
            <span v-else>{{ row.relation_type || '---' }}</span>
          </template>
        </vxe-column>
        <vxe-column field="is_system" title="Hệ thống" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.is_system" class="status-badge finalized">System</span>
            <span v-else class="status-badge draft">User</span>
          </template>
        </vxe-column>
        <vxe-column title="Hành động" width="150" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <button v-if="editingId === row.id" @click="updateRole(row)" class="btn-action btn-save">Lưu</button>
              <button v-else @click="editingId = row.id" class="btn-action btn-edit">Sửa</button>

              <button v-if="!row.is_system" @click="deleteRole(row.id)" class="btn-action btn-delete">Xóa</button>
              <span v-else title="Role hệ thống không thể xóa" class="text-muted px-2 cursor-not-allowed">🔒</span>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa vai trò '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '@/utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'AdminRoles',
  components: { ConfirmModal },
  mixins: [errorHandlingMixin, FilterableTableMixin],
  data() {
    return {
      roles: [],
      newRole: { name: '', slug: '', description: '', relation_type: '' },
      editingId: null,
      filters: { search: '' },
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  computed: {
    filteredRoles() {
      return this.filterArray(this.roles, this.filters, {
        search: { type: 'text', fields: ['name', 'slug'] }
      });
    }
  },
  watch: {
  },
  mounted() {
    this.fetchRoles();
  },
  methods: {
    async fetchRoles() {
      try {
        const res = await axios.get(`${API_URL}/roles/`);
        this.roles = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách vai trò');
      }
    },
    async addRole() {
      if (!this.newRole.name) {
        this.showWarning('Vui lòng nhập tên vai trò', 'Thiếu thông tin');
        return;
      }
      try {
        await axios.post(`${API_URL}/roles/`, this.newRole);
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
          await axios.delete(`${API_URL}/roles/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchRoles();
        } catch (e) {
          this.showDeleteModal = false;
          this.showError(e, 'Lỗi xóa vai trò');
        }
      }
    },
    async updateRole(role) {
      try {
        await axios.put(`${API_URL}/roles/${role.id}/`, role);
        this.editingId = null;
      } catch (e) {
        this.showError(e, 'Lỗi cập nhật vai trò');
      }
    }
  }
}
</script>

<style scoped>
.data-table-vxe {
  margin-top: 10px;
}
</style>

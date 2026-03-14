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
        <button @click="addRole" class="btn-action btn-create btn-icon-only" :disabled="!canCreate"
          :title="canCreate ? 'Thêm Vai trò mới' : 'Không có quyền tạo'">
          <SvgIcon name="plus" size="sm" />
        </button>
      </div>
    </div>

    <div class="filter-bar admin-row align-end gap-md mb-4">
      <div class="filter-group" style="flex: 1; min-width: 300px;">
        <label class="premium-label">
          <SvgIcon name="search" size="xs" /> Tìm kiếm
        </label>
        <div class="premium-input-wrapper">
          <input v-model="filters.search" placeholder="Tìm theo tên hoặc mã..." class="filter-control premium-input">
        </div>
      </div>

      <div class="filter-group" style="flex: 0 0 auto;">
        <label class="premium-label" style="visibility: hidden;">&nbsp;</label>
        <div class="premium-input-wrapper">
          <button class="btn-action btn-secondary flex items-center gap-2" @click="resetFilters" title="Đặt lại bộ lọc">
            <SvgIcon name="x" size="sm" /> <span>Đặt lại</span>
          </button>
        </div>
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
            <span v-if="row.is_system" class="admin-badge badge-admin">System</span>
            <span v-else class="admin-badge badge-inactive">Custom</span>
          </template>
        </vxe-column>
        <vxe-column title="Hành động" width="160" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <template v-if="editingId === row.id">
                <button @click="updateRole(row)" class="btn-action btn-save btn-icon-only" title="Lưu thay đổi">
                  <SvgIcon name="save" size="sm" />
                </button>
                <button @click="editingId = null" class="btn-action btn-secondary btn-icon-only" title="Hủy bỏ">
                  <SvgIcon name="x" size="sm" />
                </button>
              </template>
              <template v-else>
                <button @click="editingId = row.id" class="btn-action btn-edit btn-icon-only" :disabled="!canChange"
                  :title="canChange ? 'Sửa' : 'Không có quyền sửa'">
                  <SvgIcon name="edit" size="sm" />
                </button>
                <button :disabled="row.is_system || !canDelete" @click="deleteRole(row.id)"
                  class="btn-action btn-delete btn-icon-only"
                  :title="row.is_system ? 'Dữ liệu hệ thống, không thể xóa' : (canDelete ? 'Xóa' : 'Không có quyền xóa')">
                  <SvgIcon name="trash" size="sm" />
                </button>
              </template>
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
import MasterService from '@/services/master.service';
import { useAuthStore } from '@/store/auth.store';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '@/utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'AdminRoles',
  title: 'Quản lý Vai trò & Quyền',
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
      deleteTargetName: '',
      authStore: useAuthStore()
    }
  },
  computed: {
    filteredRoles() {
      return this.filterArray(this.roles, this.filters, {
        search: { type: 'text', fields: ['name', 'slug'] }
      });
    },
    canCreate() { return this.authStore.hasPermission('document_automation.add_role'); },
    canChange() { return this.authStore.hasPermission('document_automation.change_role'); },
    canDelete() { return this.authStore.hasPermission('document_automation.delete_role'); },
  },
  mounted() {
    this.fetchRoles();
  },
  methods: {
    async fetchRoles() {
      try {
        const res = await MasterService.getRoles();
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
        await MasterService.createRole(this.newRole);
        this.newRole.name = '';
        this.newRole.slug = '';
        this.newRole.description = '';
        this.fetchRoles();
        this.showSuccess('Thêm vai trò thành công!');
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
          await MasterService.deleteRole(this.deleteTargetId);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchRoles();
          this.showSuccess('Đã xóa vai trò!');
        } catch (e) {
          this.showDeleteModal = false;
          this.showError(e, 'Lỗi xóa vai trò');
        }
      }
    },
    async updateRole(role) {
      try {
        await MasterService.updateRole(role.id, role);
        this.editingId = null;
        this.showSuccess('Cập nhật thành công!');
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

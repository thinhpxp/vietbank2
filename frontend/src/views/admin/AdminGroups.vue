<template>
  <div class="admin-page">
    <h2>Quản lý Nhóm Thông tin</h2>
    <div class="admin-panel">
      <h4>Thêm nhóm mới</h4>
      <div class="admin-row">
        <input v-model="newGroup.name" placeholder="Tên nhóm mới" class="admin-input">
        <input v-model="newGroup.slug" placeholder="Mã (Slug - Tùy chọn)" class="admin-input">
        <select v-model="newGroup.layout_position" class="admin-input">
          <option value="LEFT">Cột Trái</option>
          <option value="RIGHT">Cột Phải</option>
        </select>
        <input v-model="newGroup.note" placeholder="Ghi chú (Tùy chọn)" class="admin-input">
        <input v-model.number="newGroup.order" placeholder="Thứ tự" type="number" style="max-width: 100px"
          class="admin-input">
        <button @click="addGroup" class="btn-action btn-create btn-icon-only" title="Thêm Nhóm mới">
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
      <vxe-table border round :data="filteredGroups" :row-config="{ isHover: true }"
        :column-config="{ resizable: true }" :sort-config="{ trigger: 'cell' }">
        <vxe-column field="id" title="ID" width="60" sortable></vxe-column>
        <vxe-column field="name" title="Tên Nhóm" min-width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.name" class="vxe-input-minimal">
            <span v-else>{{ row.name }}</span>
          </template>
        </vxe-column>
        <vxe-column field="slug" title="Mã (Slug)" width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.slug" class="vxe-input-minimal"
              placeholder="vd: thong-tin-chung">
            <span v-else><code>{{ row.slug || '---' }}</code></span>
          </template>
        </vxe-column>
        <vxe-column field="layout_position" title="Vị trí" width="120" sortable>
          <template #default="{ row }">
            <select v-if="editingId === row.id" v-model="row.layout_position" class="vxe-input-minimal">
              <option value="LEFT">Cột Trái</option>
              <option value="RIGHT">Cột Phải</option>
            </select>
            <span v-else>
              <span v-if="row.layout_position === 'RIGHT'" class="status-badge draft">Cột Phải</span>
              <span v-else class="status-badge finalized">Cột Trái</span>
            </span>
          </template>
        </vxe-column>
        <vxe-column field="note" title="Ghi chú" min-width="150">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.note" class="vxe-input-minimal">
            <span v-else>{{ row.note }}</span>
          </template>
        </vxe-column>
        <vxe-column field="order" title="Thứ tự" width="100" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model.number="row.order" type="number" class="vxe-input-minimal">
            <span v-else>{{ row.order }}</span>
          </template>
        </vxe-column>
        <vxe-column title="Loại đối tượng áp dụng" min-width="200">
          <template #default="{ row }">
            <div v-if="editingId === row.id">
              <div v-for="type in objectTypes" :key="type.id">
                <label class="admin-checkbox-label">
                  <input type="checkbox" :value="type.id" v-model="row.allowed_object_types">
                  {{ type.name }}
                </label>
              </div>
            </div>
            <div v-else>
              <div class="flex flex-col gap-1 items-start">
                <span v-for="tid in row.allowed_object_types.slice(0, 2)" :key="tid" class="badge badge-inactive">
                  {{objectTypes.find(t => t.id === tid)?.name || tid}}
                </span>
                <span v-if="row.allowed_object_types.length > 2" class="badge badge-inactive" style="opacity: 0.7"
                  :title="row.allowed_object_types.map(tid => objectTypes.find(t => t.id === tid)?.name || tid).join(', ')">
                  +{{ row.allowed_object_types.length - 2 }} more...
                </span>
              </div>
            </div>
          </template>
        </vxe-column>
        <vxe-column title="Hiển thị ở Form" min-width="200">
          <template #default="{ row }">
            <div v-if="editingId === row.id">
              <div v-for="f in allForms" :key="f.id">
                <label class="admin-checkbox-label">
                  <input type="checkbox" :value="f.id" v-model="row.allowed_forms"> {{ f.name }}
                </label>
              </div>
            </div>
            <div v-else>
              <div class="flex flex-col gap-1 items-start">
                <span v-for="fid in row.allowed_forms.slice(0, 2)" :key="fid" class="badge badge-inactive">
                  {{allForms.find(f => f.id === fid)?.name || fid}}
                </span>
                <span v-if="row.allowed_forms.length > 2" class="badge badge-inactive" style="opacity: 0.7"
                  :title="row.allowed_forms.map(fid => allForms.find(f => f.id === fid)?.name || fid).join(', ')">
                  +{{ row.allowed_forms.length - 2 }} more...
                </span>
              </div>
            </div>
          </template>
        </vxe-column>
        <vxe-column title="Hành động" width="160" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <template v-if="editingId === row.id">
                <button @click="updateGroup(row)" class="btn-action btn-save btn-icon-only" title="Lưu thay đổi">
                  <SvgIcon name="save" size="sm" />
                </button>
                <button @click="editingId = null" class="btn-action btn-secondary btn-icon-only" title="Hủy bỏ">
                  <SvgIcon name="x" size="sm" />
                </button>
              </template>
              <template v-else>
                <button @click="editingId = row.id" class="btn-action btn-edit btn-icon-only" :disabled="!canChange"
                  :title="canChange ? 'Chỉnh sửa' : 'Không có quyền sửa'">
                  <SvgIcon name="edit" size="sm" />
                </button>
                <button @click="deleteGroup(row.id)" class="btn-action btn-delete btn-icon-only" :disabled="!canDelete"
                  :title="canDelete ? 'Xóa' : 'Không có quyền xóa'">
                  <SvgIcon name="trash" size="sm" />
                </button>
              </template>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa nhóm '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
  </div>
</template>

<script>
import MasterService from '@/services/master.service';
import auth from '@/store/auth';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '@/utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'AdminGroups',
  title: 'Quản lý Nhóm thông tin',
  components: { ConfirmModal },
  mixins: [errorHandlingMixin, FilterableTableMixin],
  data() {
    return {
      groups: [],
      objectTypes: [],
      allForms: [],
      newGroup: { name: '', slug: '', order: 0, note: '', allowed_forms: [], layout_position: 'LEFT', allowed_object_types: [] },
      editingId: null,
      filters: { search: '' },
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  computed: {
    filteredGroups() {
      return this.filterArray(this.groups, this.filters, {
        search: { type: 'text', fields: ['name', 'slug'] }
      });
    },
    canCreate() { return auth.hasPermission('auth.add_group'); },
    canChange() { return auth.hasPermission('auth.change_group'); },
    canDelete() { return auth.hasPermission('auth.delete_group'); },
  },
  async mounted() {
    await this.fetchGroups();
    await this.fetchForms();
    await this.fetchObjectTypes();
  },
  methods: {
    getFormNames(ids) {
      if (!ids || ids.length === 0) return 'Chưa gán (Ẩn)';
      return this.allForms
        .filter(f => ids.includes(f.id))
        .map(f => f.name)
        .join(', ');
    },
    async fetchGroups() {
      try {
        const groupsRes = await MasterService.getGroups();
        this.groups = groupsRes.data.sort((a, b) => a.order - b.order);
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách nhóm');
      }
    },
    async fetchForms() {
      try {
        const res = await MasterService.getFormViews();
        this.allForms = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách Form');
      }
    },
    async fetchObjectTypes() {
      try {
        const res = await MasterService.getObjectTypes();
        this.objectTypes = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải loại đối tượng');
      }
    },
    async addGroup() {
      if (!this.newGroup.name) return;
      try {
        await MasterService.createGroup(this.newGroup);
        this.newGroup.name = '';
        this.newGroup.slug = '';
        this.newGroup.order = 0;
        this.newGroup.allowed_object_types = [];
        this.newGroup.layout_position = 'LEFT';
        this.newGroup.allowed_forms = [];
        this.fetchGroups();
        this.showSuccess('Đã thêm nhóm mới thành công!');
      } catch (e) {
        this.showError(e, 'Lỗi thêm nhóm mới');
      }
    },
    deleteGroup(id) {
      const grp = this.groups.find(g => g.id === id);
      this.deleteTargetId = id;
      this.deleteTargetName = grp ? grp.name : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        try {
          await MasterService.deleteGroup(this.deleteTargetId);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchGroups();
          this.showSuccess('Đã xóa nhóm thành công!');
        } catch (e) {
          this.showDeleteModal = false;
          this.showError(e, 'Lỗi xóa nhóm');
        }
      }
    },
    async updateGroup(grp) {
      try {
        await MasterService.updateGroup(grp.id, grp);
        this.editingId = null;
        this.showSuccess('Cập nhật nhóm thành công!');
      } catch (e) {
        this.showError(e, 'Lỗi cập nhật nhóm');
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
  align-items: center;
}

.action-group {
  display: flex;
  gap: 5px;
}

.form-selector {
  max-height: 80px;
  overflow-y: auto;
  font-size: 0.8em;
  border: 1px solid #eee;
  padding: 5px;
}

.form-selector label {
  display: block;
}
</style>
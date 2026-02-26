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
        <button @click="addGroup" class="btn-action btn-create">Thêm Nhóm</button>
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
              <span v-if="!row.allowed_object_types || row.allowed_object_types.length === 0" class="badge-form">Tất
                cả</span>
              <div class="flex gap-2 flex-wrap">
                <span v-for="tid in row.allowed_object_types" :key="tid" class="badge-form">
                  {{objectTypes.find(t => t.id === tid)?.name || tid}}
                </span>
              </div>
            </div>
          </template>
        </vxe-column>
        <vxe-column title="Hiển thị ở Form" min-width="200">
          <template #default="{ row }">
            <div v-if="editingId === row.id" class="form-selector">
              <label v-for="f in allForms" :key="f.id" class="admin-checkbox-label">
                <input type="checkbox" :value="f.id" v-model="row.allowed_forms"> {{ f.name }}
              </label>
            </div>
            <span v-else>{{ getFormNames(row.allowed_forms) }}</span>
          </template>
        </vxe-column>
        <vxe-column title="Hành động" width="150" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <button v-if="editingId === row.id" @click="updateGroup(row)" class="btn-action btn-save">Lưu</button>
              <button v-else @click="editingId = row.id" class="btn-action btn-edit">Sửa</button>
              <button @click="deleteGroup(row.id)" class="btn-action btn-delete">Xóa</button>
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
import axios from 'axios';
import { API_URL } from '@/store/auth';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '@/utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  components: { ConfirmModal },
  mixins: [errorHandlingMixin, FilterableTableMixin],
  data() {
    return {
      groups: [],
      objectTypes: [],  // NEW
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
    }
  },
  watch: {
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
        const groupsRes = await axios.get(`${API_URL}/groups/`);
        this.groups = groupsRes.data.sort((a, b) => a.order - b.order);
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách nhóm');
      }
    },
    async fetchForms() {
      try {
        const res = await axios.get(`${API_URL}/form-views/`);
        this.allForms = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách Form');
      }
    },
    async fetchObjectTypes() {
      try {
        const res = await axios.get(`${API_URL}/object-types/`);
        this.objectTypes = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải loại đối tượng');
      }
    },
    async addGroup() {
      if (!this.newGroup.name) return;
      try {
        await axios.post(`${API_URL}/groups/`, this.newGroup);
        this.newGroup.name = '';
        this.newGroup.slug = '';
        this.newGroup.order = 0;
        this.newGroup.allowed_object_types = [];
        this.newGroup.layout_position = 'LEFT';
        this.newGroup.object_type = null;
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
          await axios.delete(`${API_URL}/groups/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchGroups();
          this.showSuccess('Đã xóa nhóm thành công!');
        } catch (e) {
          this.showDeleteModal = false; // Đóng confirm modal trước khi hiện lỗi
          this.showError(e, 'Lỗi xóa nhóm');
        }
      }
    },
    async updateGroup(grp) {
      try {
        await axios.put(`${API_URL}/groups/${grp.id}/`, grp);
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
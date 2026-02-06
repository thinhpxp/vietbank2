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

    <div class="ui-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên Nhóm</th>
            <th>Mã (Slug)</th>
            <th>Vị trí</th>
            <th>Ghi chú</th>
            <th>Thứ tự</th>
            <th>Loại đối tượng áp dụng</th>
            <th>Hiển thị ở Form</th>
            <th>Hành động</th>
          </tr>
        </thead>

        <tbody class="tbody">
          <tr v-for="grp in groups" :key="grp.id">
            <td>{{ grp.id }}</td>
            <td>
              <input v-if="editingId === grp.id" v-model="grp.name" style="width: 35%">
              <span v-else>{{ grp.name }}</span>
            </td>
            <td>
              <input v-if="editingId === grp.id" v-model="grp.slug" style="width: 90%"
                placeholder="vd: thong-tin-chung">
              <span v-else><code>{{ grp.slug || '---' }}</code></span>
            </td>
            <td>
              <select v-if="editingId === grp.id" v-model="grp.layout_position">
                <option value="LEFT">Cột Trái</option>
                <option value="RIGHT">Cột Phải</option>
              </select>
              <span v-else>
                <span v-if="grp.layout_position === 'RIGHT'" class="badge badge-warning">Cột Phải</span>
                <span v-else class="badge badge-info">Cột Trái</span>
              </span>
            </td>
            <td>
              <input v-if="editingId === grp.id" v-model="grp.note" style="width: 60%">
              <span v-else>{{ grp.note }}</span>
            </td>
            <td>
              <input v-if="editingId === grp.id" v-model.number="grp.order" type="number" style="width:50px">
              <span v-else>{{ grp.order }}</span>
            </td>
            <td style="min-width: 150px;">
              <!-- Object Types Column -->
              <div v-if="editingId === grp.id">
                <div v-for="type in objectTypes" :key="type.id">
                  <label>
                    <input type="checkbox" :value="type.id" v-model="grp.allowed_object_types">
                    {{ type.name }}
                  </label>
                </div>
              </div>
              <div v-else>
                <span v-if="!grp.allowed_object_types || grp.allowed_object_types.length === 0" class="badge-all">Tất
                  cả</span>
                <span v-else v-for="tid in grp.allowed_object_types" :key="tid" class="badge">
                  {{objectTypes.find(t => t.id === tid)?.name || tid}}
                </span>
              </div>
            </td>
            <td>
              <div v-if="editingId === grp.id" class="admin-form-selector">
                <label v-for="f in allForms" :key="f.id">
                  <input type="checkbox" :value="f.id" v-model="grp.allowed_forms"> {{ f.name }}
                </label>
              </div>
              <span v-else>{{ getFormNames(grp.allowed_forms) }}</span>
            </td>
            <td>
              <div class="flex gap-2">
                <button v-if="editingId === grp.id" @click="updateGroup(grp)" class="btn-action btn-save">Lưu</button>
                <button v-else @click="editingId = grp.id" class="btn-action btn-edit">Sửa</button>
                <button @click="deleteGroup(grp.id)" class="btn-action btn-delete">Xóa</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
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
import { makeTableResizable } from '../../utils/resizable-table';
import { errorHandlingMixin } from '@/utils/errorHandler';

export default {
  components: { ConfirmModal },
  mixins: [errorHandlingMixin],
  data() {
    return {
      groups: [],
      objectTypes: [],  // NEW
      allForms: [],
      newGroup: { name: '', slug: '', order: 0, note: '', allowed_forms: [], layout_position: 'LEFT', allowed_object_types: [] },
      editingId: null,
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  async mounted() {
    await this.fetchGroups();
    await this.fetchForms();
    await this.fetchObjectTypes();  // NEW
    this.initResizable();
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
        this.$nextTick(() => this.initResizable());
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách nhóm');
      }
    },
    initResizable() {
      const table = this.$el.querySelector('.data-table');
      if (table) {
        makeTableResizable(table, 'admin-groups');
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
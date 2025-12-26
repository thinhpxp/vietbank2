<template>
  <div>
    <h2>Quản lý Nhóm Thông tin</h2>
    <div class="actions">
      <input v-model="newGroup.name" placeholder="Tên nhóm mới">
      <input v-model="newGroup.note" placeholder="Ghi chú (Tùy chọn)" style="flex: 2">
      <input v-model.number="newGroup.order" placeholder="Thứ tự" type="number" style="width: 60px">
      <button @click="addGroup" class="btn-create">Thêm Nhóm</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Tên Nhóm</th>
          <th>Ghi chú</th>
          <th>Thứ tự</th>
          <th>Hiển thị ở Form</th>
          <th>Hành động</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="grp in groups" :key="grp.id">
          <td>{{ grp.id }}</td>
          <td>
            <input v-if="editingId === grp.id" v-model="grp.name" style="width: 35%">
            <span v-else>{{ grp.name }}</span>
          </td>
          <td>
            <input v-if="editingId === grp.id" v-model="grp.note" style="width: 60%">
            <span v-else>{{ grp.note }}</span>
          </td>
          <td>
            <input v-if="editingId === grp.id" v-model.number="grp.order" type="number" style="width:50px">
            <span v-else>{{ grp.order }}</span>
          </td>
          <td>
            <div v-if="editingId === grp.id" class="form-selector">
              <label v-for="f in allForms" :key="f.id">
                <input type="checkbox" :value="f.id" v-model="grp.allowed_forms"> {{ f.name }}
              </label>
            </div>
            <span v-else>{{ getFormNames(grp.allowed_forms) }}</span>
          </td>
          <td>
            <button v-if="editingId === grp.id" @click="updateGroup(grp)">Lưu</button>
            <button v-else @click="editingId = grp.id">Sửa</button>
            <button @click="deleteGroup(grp.id)" class="btn-delete">Xóa</button>
          </td>
        </tr>
      </tbody>
    </table>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa nhóm '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
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
      groups: [],
      allForms: [],
      newGroup: { name: '', order: 0, note: '', allowed_forms: [] },
      editingId: null,
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  mounted() {
    this.fetchGroups();
    this.fetchForms();
  },
  methods: {
    async fetchForms() {
      const res = await axios.get('http://127.0.0.1:8000/api/form-views/');
      this.allForms = res.data;
    },
    getFormNames(ids) {
      if (!ids || ids.length === 0) return 'Tất cả';
      return this.allForms
        .filter(f => ids.includes(f.id))
        .map(f => f.name)
        .join(', ');
    },
    async fetchGroups() {
      const res = await axios.get('http://127.0.0.1:8000/api/groups/');
      this.groups = res.data;
    },
    async addGroup() {
      if (!this.newGroup.name) return;
      await axios.post('http://127.0.0.1:8000/api/groups/', this.newGroup);
      this.newGroup.name = ''; this.fetchGroups();
    },
    deleteGroup(id) {
      const grp = this.groups.find(g => g.id === id);
      this.deleteTargetId = id;
      this.deleteTargetName = grp ? grp.name : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        await axios.delete(`http://127.0.0.1:8000/api/groups/${this.deleteTargetId}/`);
        this.showDeleteModal = false;
        this.deleteTargetId = null;
        this.fetchGroups();
      }
    },
    async updateGroup(grp) {
      await axios.put(`http://127.0.0.1:8000/api/groups/${grp.id}/`, grp);
      this.editingId = null;
    }
  }
}
</script>
<style scoped>
/* CSS dùng chung có thể để ở App.vue, ở đây viết gọn */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  background: white;
}

.data-table th,
.data-table td {
  padding: 10px;
  border: 1px solid #ddd;
}

.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.btn-create {
  background: #42b983;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
}

.btn-delete {
  background: #e74c3c;
  color: white;
  border: none;
  margin-left: 5px;
  cursor: pointer;
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
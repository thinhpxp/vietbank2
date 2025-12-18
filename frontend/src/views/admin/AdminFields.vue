<template>
  <div>
    <h2>Quản lý Trường Dữ liệu</h2>

    <!-- Form thêm mới -->
    <div class="add-box">
      <h4>Thêm trường mới</h4>
      <div class="row">
        <input v-model="newField.label" placeholder="Nhãn hiển thị (VD: Số tiền)">
        <input v-model="newField.placeholder_key" placeholder="Key (VD: so_tien)">
        <input v-model="newField.note" placeholder="Ghi chú về trường thông tin này">
      </div>
      <div class="row">
        <select v-model="newField.data_type">
          <option value="TEXT">Văn bản</option>
          <option value="NUMBER">Số</option>
          <option value="DATE">Ngày</option>
          <option value="CHECKBOX">Hộp kiểm</option>
        </select>
        <select v-model="newField.group">
          <option :value="null">-- Chọn nhóm --</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
        <button @click="addField" class="btn-create">Thêm</button>
      </div>
    </div>

    <!-- Danh sách -->
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Key</th>
          <th>Nhãn</th>
          <th>Ghi chú</th>
          <th>Loại</th>
          <th>Nhóm</th>
          <th>Hành động</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="f in fields" :key="f.id">
          <td>{{ f.id }}</td>
          <td>
            <input v-if="editingId === f.id" v-model="f.placeholder_key" style="width: 100%">
            <span v-else>{{ f.placeholder_key }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" v-model="f.label" style="width: 100%">
            <span v-else>{{ f.label }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" v-model="f.note" style="width: 100%">
            <span v-else>{{ f.note }}</span>
          </td>
          <td>
            <select v-if="editingId === f.id" v-model="f.data_type">
              <option value="TEXT">Văn bản</option>
              <option value="NUMBER">Số</option>
              <option value="DATE">Ngày</option>
              <option value="CHECKBOX">Hộp kiểm</option>
            </select>
            <span v-else>{{ f.data_type }}</span>
          </td>
          <td>
            <select v-if="editingId === f.id" v-model="f.group">
              <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
            </select>
            <span v-else>{{ f.group_name }}</span>
          </td>
          <td>
            <button v-if="editingId === f.id" @click="updateField(f)" class="btn-create">Lưu</button>
            <button v-else @click="editingId = f.id">Sửa</button>
            <button @click="deleteField(f.id)" class="btn-delete">Xóa</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      fields: [], groups: [],
      editingId: null,
      // make sure `note` is present here so Vue makes it reactive
      newField: { label: '', placeholder_key: '', note: '', data_type: 'TEXT', group: null }
    }
  },
  mounted() { this.fetchData(); },
  methods: {
    async fetchData() {
      const [resFields, resGroups] = await Promise.all([
        axios.get('http://127.0.0.1:8000/api/fields/'),
        axios.get('http://127.0.0.1:8000/api/groups/')
      ]);
      this.fields = resFields.data;
      this.groups = resGroups.data;
    },
    async addField() {
      if(!this.newField.group) return alert('Vui lòng chọn nhóm!');
      try {
        await axios.post('http://127.0.0.1:8000/api/fields/', this.newField);
        this.fetchData();
        // Reset form (giữ lại nhóm để nhập tiếp cho nhanh)
        this.newField.label = ''; this.newField.placeholder_key = '';
        // also clear the note so the input shows its placeholder again
        this.newField.note = '';
      } catch(e) { alert('Lỗi: ' + JSON.stringify(e.response.data)); }
    },
    async updateField(field) {
      try {
        await axios.put(`http://127.0.0.1:8000/api/fields/${field.id}/`, field);
        this.editingId = null;
        await this.fetchData(); // Refresh data to show updated group name etc.
      } catch (e) {
        alert('Lỗi khi cập nhật: ' + JSON.stringify(e.response.data));
      }
    },
    async deleteField(id) {
      if(confirm('Xóa trường này?')) {
        await axios.delete(`http://127.0.0.1:8000/api/fields/${id}/`);
        this.fetchData();
      }
    }
  }
}
</script>
<style scoped>
.add-box { background: #eee; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
.row { display: flex; gap: 10px; margin-bottom: 10px; }
.row input, .row select { padding: 8px; flex: 1; }
.btn-create { background: #42b983; color: white; border: none; padding: 8px 15px; cursor: pointer; }
.data-table { width: 100%; border-collapse: collapse; background: white; }
.data-table th, .data-table td { padding: 10px; border: 1px solid #ddd; }
.btn-delete { background: #e74c3c; color: white; border: none; padding: 5px; cursor: pointer; margin-left: 5px; }
</style>
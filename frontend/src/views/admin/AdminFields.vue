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
        <input v-model.number="newField.order" type="number" placeholder="Thứ tự (0)" style="max-width: 80px">
        <input v-model.number="newField.width_cols" type="number" min="1" max="12" placeholder="Độ rộng (1-12)" style="max-width: 100px">
        <input v-model="newField.css_class" placeholder="CSS Class (VD: text-red)">
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
          <th @click="toggleSort('id')" class="sortable">ID <span v-if="sortBy==='id'">{{sortDesc?'▼':'▲'}}</span></th>
          <th @click="toggleSort('order')" class="sortable" width="50">Thứ tự <span v-if="sortBy==='order'">{{sortDesc?'▼':'▲'}}</span></th>
          <th @click="toggleSort('placeholder_key')" class="sortable">Key <span v-if="sortBy==='placeholder_key'">{{sortDesc?'▼':'▲'}}</span></th>
          <th @click="toggleSort('label')" class="sortable">Nhãn <span v-if="sortBy==='label'">{{sortDesc?'▼':'▲'}}</span></th>
          <th @click="toggleSort('data_type')" class="sortable">Loại <span v-if="sortBy==='data_type'">{{sortDesc?'▼':'▲'}}</span></th>
          <th @click="toggleSort('group')" class="sortable">Nhóm <span v-if="sortBy==='group'">{{sortDesc?'▼':'▲'}}</span></th>
          <th width="50">Rộng</th>
          <th>CSS</th>
          <th>Hành động</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="f in sortedFields" :key="f.id">
          <td>{{ f.id }}</td>
          <td>
             <input v-if="editingId === f.id" v-model.number="f.order" type="number" style="width: 40px">
             <span v-else>{{ f.order }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" v-model="f.placeholder_key" style="width: 100%">
            <span v-else>{{ f.placeholder_key }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" v-model="f.label" style="width: 100%">
            <span v-else>{{ f.label }}</span>
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
             <input v-if="editingId === f.id" v-model.number="f.width_cols" type="number" min="1" max="12" style="width: 40px">
             <span v-else>{{ f.width_cols }}</span>
          </td>
          <td>
             <input v-if="editingId === f.id" v-model="f.css_class" style="width: 80px">
             <span v-else>{{ f.css_class }}</span>
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
      newField: { 
          label: '', placeholder_key: '', note: '', data_type: 'TEXT', group: null,
          order: 0, width_cols: 12, css_class: '' 
      },
      // State cho sorting
      sortBy: 'order',
      sortDesc: false
    }
  },
  mounted() { this.fetchData(); },
  computed: {
    sortedFields() {
      // Logic sort client-side
      return [...this.fields].sort((a, b) => {
        let valA = a[this.sortBy];
        let valB = b[this.sortBy];
        
        // Xử lý trường hợp null/undefined
        if (valA === null || valA === undefined) valA = '';
        if (valB === null || valB === undefined) valB = '';

        // Nếu sort theo group, so sánh group_name
        if (this.sortBy === 'group') {
            valA = a.group_name || '';
            valB = b.group_name || '';
        }

        if (valA < valB) return this.sortDesc ? 1 : -1;
        if (valA > valB) return this.sortDesc ? -1 : 1;
        return 0;
      });
    }
  },
  methods: {
    toggleSort(column) {
      if (this.sortBy === column) {
        this.sortDesc = !this.sortDesc;
      } else {
        this.sortBy = column;
        this.sortDesc = false;
      }
    },
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
        // Reset form
        this.newField = { 
            label: '', placeholder_key: '', note: '', data_type: 'TEXT', group: this.newField.group, // Giữ lại group
            order: 0, width_cols: 12, css_class: '' 
        };
      } catch(e) { alert('Lỗi: ' + JSON.stringify(e.response.data)); }
    },
    async updateField(field) {
      try {
        await axios.put(`http://127.0.0.1:8000/api/fields/${field.id}/`, field);
        this.editingId = null;
        await this.fetchData();
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
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { background-color: #f1f1f1; }
</style>
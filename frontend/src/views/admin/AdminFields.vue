<template>
  <div class="admin-page">
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
        <input v-model.number="newField.width_cols" type="number" min="1" max="12" placeholder="Độ rộng (1-12)"
          style="max-width: 100px">
        <input v-model="newField.css_class" placeholder="CSS Class (VD: text-red)">
        <input v-model="newField.default_value" placeholder="Giá trị mặc định">
      </div>
      <div class="row">
        <select v-model="newField.data_type">
          <option value="TEXT">Văn bản</option>
          <option value="TEXTAREA">Đoạn văn bản</option>
          <option value="NUMBER">Số</option>
          <option value="DATE">Ngày</option>
          <option value="CHECKBOX">Hộp kiểm</option>
        </select>
        <label style="display: flex; align-items: center; gap: 5px; font-size: 0.85em; cursor: pointer;">
          <input type="checkbox" v-model="newField.use_digit_grouping"> Tách nghìn
        </label>
        <label style="display: flex; align-items: center; gap: 5px; font-size: 0.85em; cursor: pointer;">
          <input type="checkbox" v-model="newField.show_amount_in_words"> Hiện chữ
        </label>
        <select v-model="newField.group">
          <option :value="null">-- Chọn nhóm --</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
        <button @click="addField" class="btn-action btn-create">Thêm</button>
      </div>
    </div>

    <!-- Bộ lọc -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>Tìm kiếm</label>
        <input v-model="filters.search" placeholder="Nhãn hoặc Key..." class="filter-control">
      </div>
      <div class="filter-group">
        <label>Nhóm</label>
        <select v-model="filters.group" class="filter-control">
          <option :value="null">-- Tất cả nhóm --</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Loại dữ liệu</label>
        <select v-model="filters.dataType" class="filter-control">
          <option :value="null">-- Tất cả loại --</option>
          <option value="TEXT">Văn bản</option>
          <option value="TEXTAREA">Đoạn văn bản</option>
          <option value="NUMBER">Số</option>
          <option value="DATE">Ngày</option>
          <option value="CHECKBOX">Hộp kiểm</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Loại đối tượng</label>
        <select v-model="filters.objectType" class="filter-control">
          <option :value="null">-- Tất cả đối tượng --</option>
          <option v-for="t in objectTypes" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>
      <button class="btn-action btn-secondary" @click="resetFilters">Đặt lại</button>
    </div>

    <!-- Danh sách -->
    <table class="data-table" ref="resizableTable">
      <thead>
        <tr>
          <th @click="toggleSort('id')" class="sortable">ID <span v-if="sortBy === 'id'">{{ sortDesc ? '▼' : '▲'
              }}</span></th>
          <th @click="toggleSort('order')" class="sortable" width="50">Thứ tự <span v-if="sortBy === 'order'">{{
            sortDesc ? '▼' : '▲' }}</span></th>
          <th @click="toggleSort('placeholder_key')" class="sortable">Key <span v-if="sortBy === 'placeholder_key'">{{
            sortDesc ? '▼' : '▲' }}</span></th>
          <th @click="toggleSort('label')" class="sortable">Nhãn <span v-if="sortBy === 'label'">{{ sortDesc ? '▼' : '▲'
              }}</span></th>
          <th @click="toggleSort('data_type')" class="sortable">Loại <span v-if="sortBy === 'data_type'">{{ sortDesc ?
            '▼' : '▲' }}</span></th>
          <th @click="toggleSort('group')" class="sortable">Nhóm <span v-if="sortBy === 'group'">{{ sortDesc ? '▼' : '▲'
              }}</span></th>
          <th width="50">Rộng</th>
          <th>CSS</th>
          <th>Mặc định</th>
          <th>Tách nghìn</th>
          <th>Hiện chữ</th>
          <th>Form</th>
          <th>Loại đối tượng</th>
          <th>Hành động</th>
        </tr>
      </thead>
      <tbody class="tbody">
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
              <option value="TEXTAREA">Đoạn văn bản</option>
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
            <input v-if="editingId === f.id" v-model.number="f.width_cols" type="number" min="1" max="12"
              style="width: 40px">
            <span v-else>{{ f.width_cols }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" v-model="f.css_class" style="width: 80px">
            <span v-else>{{ f.css_class }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" v-model="f.default_value" style="width: 100px">
            <span v-else>{{ f.default_value }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" type="checkbox" v-model="f.use_digit_grouping">
            <span v-else>{{ f.use_digit_grouping ? '✅' : '❌' }}</span>
          </td>
          <td>
            <input v-if="editingId === f.id" type="checkbox" v-model="f.show_amount_in_words">
            <span v-else>{{ f.show_amount_in_words ? '✅' : '❌' }}</span>
          </td>
          <td>
            <div v-if="editingId === f.id" class="form-selector">
              <label v-for="form in allForms" :key="form.id">
                <input type="checkbox" :value="form.id" v-model="f.allowed_forms"> {{ form.name }}
              </label>
            </div>
            <span v-else>{{ getFormNames(f.allowed_forms) }}</span>
          </td>
          <td>
            <div v-if="editingId === f.id" class="form-selector">
              <div v-for="type in objectTypes" :key="type.id">
                <label>
                  <input type="checkbox" :value="type.id" v-model="f.allowed_object_types">
                  {{ type.name }}
                </label>
              </div>
            </div>
            <div v-else>
              <span v-if="!f.allowed_object_types || f.allowed_object_types.length === 0" class="badge-all">Tất
                cả</span>
              <span v-else v-for="tid in f.allowed_object_types" :key="tid" class="badge">
                {{objectTypes.find(t => t.id === tid)?.name || tid}}
              </span>
            </div>
          </td>
          <td>
            <div class="action-group">
              <button v-if="editingId === f.id" @click="updateField(f)" class="btn-action btn-save">Lưu</button>
              <button v-else @click="editingId = f.id" class="btn-action btn-edit">Sửa</button>
              <button @click="copyField(f)" class="btn-action btn-copy">Copy</button>
              <button v-if="!f.is_protected" @click="deleteField(f.id)" class="btn-action btn-delete">Xóa</button>
              <span v-else class="protected-badge">🔒</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa trường '${deleteTargetLabel}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { makeTableResizable } from '../../utils/resizable-table.js';

export default {
  components: { ConfirmModal },
  data() {
    return {
      fields: [], groups: [],
      allForms: [],
      objectTypes: [],
      editingId: null,
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetLabel: '',
      filters: {
        group: null,
        dataType: null,
        objectType: null,
        search: ''
      },
      newField: {
        label: '', placeholder_key: '', note: '', data_type: 'TEXT', group: null,
        order: 0, width_cols: 12, css_class: '', default_value: '', allowed_forms: [], allowed_object_types: [],
        use_digit_grouping: false, show_amount_in_words: false
      },
      sortBy: 'order',
      sortDesc: false
    }
  },
  mounted() {
    this.fetchData();
    this.fetchForms();
    this.initResizable();
  },
  computed: {
    sortedFields() {
      let filtered = this.fields.filter(f => {
        if (this.filters.search) {
          const s = this.filters.search.toLowerCase();
          const matchLabel = f.label && f.label.toLowerCase().includes(s);
          const matchKey = f.placeholder_key && f.placeholder_key.toLowerCase().includes(s);
          if (!matchLabel && !matchKey) return false;
        }
        if (this.filters.group && f.group !== this.filters.group) return false;
        if (this.filters.dataType && f.data_type !== this.filters.dataType) return false;
        if (this.filters.objectType) {
          if (f.allowed_object_types && f.allowed_object_types.length > 0) {
            if (!f.allowed_object_types.includes(this.filters.objectType)) return false;
          }
        }
        return true;
      });

      return filtered.sort((a, b) => {
        let valA = a[this.sortBy];
        let valB = b[this.sortBy];
        if (valA === null || valA === undefined) valA = '';
        if (valB === null || valB === undefined) valB = '';
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
      const [resFields, resGroups, resTypes] = await Promise.all([
        axios.get('http://127.0.0.1:8000/api/fields/'),
        axios.get('http://127.0.0.1:8000/api/groups/'),
        axios.get('http://127.0.0.1:8000/api/object-types/')
      ]);
      this.fields = resFields.data;
      this.groups = resGroups.data;
      this.objectTypes = resTypes.data;
      this.$nextTick(() => this.initResizable());
    },
    initResizable() {
      const table = this.$refs.resizableTable;
      if (table) {
        makeTableResizable(table, 'admin-fields');
      }
    },
    async fetchForms() {
      const res = await axios.get('http://127.0.0.1:8000/api/form-views/');
      this.allForms = res.data;
    },
    getFormNames(ids) {
      if (!ids || ids.length === 0) return 'Chưa gán (Ẩn)';
      return this.allForms
        .filter(f => ids.includes(f.id))
        .map(f => f.name)
        .join(', ');
    },
    async addField() {
      if (!this.newField.group) return alert('Vui lòng chọn nhóm!');
      try {
        await axios.post('http://127.0.0.1:8000/api/fields/', this.newField);
        this.fetchData();
        this.newField = {
          label: '', placeholder_key: '', note: '', data_type: 'TEXT', group: this.newField.group,
          order: 0, width_cols: 12, css_class: '', use_digit_grouping: false, show_amount_in_words: false,
          allowed_object_types: []
        };
      } catch (e) { alert('Lỗi: ' + JSON.stringify(e.response.data)); }
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
    deleteField(id) {
      const field = this.fields.find(f => f.id === id);
      this.deleteTargetId = id;
      this.deleteTargetLabel = field ? field.label : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        await axios.delete(`http://127.0.0.1:8000/api/fields/${this.deleteTargetId}/`);
        this.showDeleteModal = false;
        this.deleteTargetId = null;
        this.fetchData();
      }
    },
    copyField(f) {
      this.newField = {
        label: f.label + ' (Copy)',
        placeholder_key: f.placeholder_key + '_copy',
        note: f.note,
        data_type: f.data_type,
        group: f.group,
        order: f.order,
        width_cols: f.width_cols,
        css_class: f.css_class,
        default_value: f.default_value,
        allowed_forms: [...f.allowed_forms],
        allowed_object_types: f.allowed_object_types ? [...f.allowed_object_types] : [],
        use_digit_grouping: f.use_digit_grouping,
        show_amount_in_words: f.show_amount_in_words
      };
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    resetFilters() {
      this.filters = { group: null, dataType: null, objectType: null, search: '' };
    }
  }
}
</script>

<style scoped>
.add-box {
  background: #eee;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 5px;
}

.row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.row input,
.row select {
  padding: 8px;
  flex: 1;
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
  min-width: 120px;
}

.form-selector label {
  display: block;
  text-align: left;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #f1f1f1;
}
</style>
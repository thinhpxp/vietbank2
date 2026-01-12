<template>
  <div class="admin-page">
    <h2>Quản lý Mẫu Hợp đồng</h2>
    <div class="actions">
      <input class="admin-input" type="text" v-model="newName" placeholder="Tên hiển thị">
      <input class="admin-input" type="text" v-model="newDesc" placeholder="Ghi chú mẫu này" style="flex: 2">

      <div class="file-upload-wrapper">
        <label for="template-file" class="btn-action btn-secondary custom-file-label">
          📁 {{ selectedFile ? 'Chọn lại' : 'Chọn tệp' }}
        </label>
        <input id="template-file" class="hidden-file-input" type="file" ref="fileInput" @change="handleFileChange">
        <span v-if="selectedFile" class="file-name-display">{{ selectedFile.name }}</span>
      </div>

      <button @click="uploadTemplate" class="btn-action btn-create">
        🚀 Upload Mẫu
      </button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Tên Mẫu</th>
          <th>Ghi chú</th>
          <th>File</th>
          <th>Hành động</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tpl in templates" :key="tpl.id">
          <td>{{ tpl.id }}</td>
          <td>{{ tpl.name }}</td>
          <td>{{ tpl.description }}</td>
          <td><a :href="tpl.file" target="_blank">Tải xuống</a></td>
          <td>
            <div class="action-group">
              <button @click="deleteTemplate(tpl.id)" class="btn-action btn-delete">Xóa</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa mẫu '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { makeTableResizable } from '../../utils/resizable-table';

export default {
  components: { ConfirmModal },
  data() {
    return {
      templates: [],
      newName: '',
      newDesc: '',
      selectedFile: null,
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  mounted() {
    this.fetchTemplates();
    this.initResizable();
  },
  methods: {
    async fetchTemplates() {
      const res = await axios.get('http://127.0.0.1:8000/api/document-templates/');
      this.templates = res.data;
      this.$nextTick(() => this.initResizable());
    },
    initResizable() {
      const table = this.$el.querySelector('.data-table');
      if (table) {
        makeTableResizable(table, 'admin-templates');
      }
    },
    handleFileChange(e) {
      this.selectedFile = e.target.files[0];
    },
    async uploadTemplate() {
      if (!this.selectedFile || !this.newName) return alert('Nhập tên và chọn file!');

      const formData = new FormData();
      formData.append('name', this.newName);
      formData.append('description', this.newDesc);
      formData.append('file', this.selectedFile);

      try {
        await axios.post('http://127.0.0.1:8000/api/document-templates/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        this.newName = ''; this.newDesc = ''; this.selectedFile = null; this.$refs.fileInput.value = '';
        this.fetchTemplates();
        alert('Upload thành công!');
      } catch (e) { alert('Lỗi upload'); }
    },
    deleteTemplate(id) {
      const tpl = this.templates.find(t => t.id === id);
      this.deleteTargetId = id;
      this.deleteTargetName = tpl ? tpl.name : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        await axios.delete(`http://127.0.0.1:8000/api/document-templates/${this.deleteTargetId}/`);
        this.showDeleteModal = false;
        this.deleteTargetId = null;
        this.fetchTemplates();
      }
    }
  }
}
</script>

<style scoped>
.file-upload-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.custom-file-label {
  display: inline-block;
  white-space: nowrap;
}

.hidden-file-input {
  display: none;
}

.file-name-display {
  font-size: 0.75rem;
  color: #666;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}


.actions {
  margin-bottom: 25px;
  display: flex;
  gap: 15px;
  align-items: flex-start;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.action-group {
  display: flex;
  gap: 5px;
}
</style>
<template>
  <div class="admin-page">
    <h2>Quản lý Mẫu Hợp đồng</h2>
    <div class="admin-panel admin-row items-center">
      <input class="admin-input" type="text" v-model="newName" placeholder="Tên hiển thị">
      <input class="admin-input" type="text" v-model="newDesc" placeholder="Ghi chú mẫu này">

      <div class="admin-file-upload">
        <label for="template-file" class="btn-action btn-secondary whitespace-nowrap">
          📁 {{ selectedFile ? 'Chọn lại' : 'Chọn tệp' }}
        </label>
        <input id="template-file" class="admin-hidden-input" type="file" ref="fileInput" @change="handleFileChange">
        <span v-if="selectedFile" class="admin-file-name">{{ selectedFile.name }}</span>
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
            <div class="flex gap-2">
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
<template>
  <div v-if="isOpen" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Xuất Hợp đồng</h3>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="modal-body">
        <p>Chọn mẫu hợp đồng bạn muốn xuất cho hồ sơ: <strong>{{ profileName }}</strong></p>

        <div v-if="loadingTemplates">Đang tải danh sách mẫu...</div>

        <select v-else v-model="selectedTemplateId" class="template-select">
          <option disabled value="">-- Chọn loại hợp đồng --</option>
          <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
            {{ tpl.name }}
          </option>
        </select>

        <div v-if="error" class="error-msg">{{ error }}</div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="close">Hủy</button>
        <button
          class="btn-download"
          @click="downloadDoc"
          :disabled="!selectedTemplateId || isProcessing"
        >
          {{ isProcessing ? 'Đang xử lý...' : 'Tải về máy (.docx)' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ContractDownloader',
  props: {
    isOpen: Boolean,      // Trạng thái mở/đóng modal
    profileId: Number,    // ID hồ sơ cần xuất
    profileName: String   // Tên hồ sơ (để hiển thị cho user biết)
  },
  emits: ['close'],
  data() {
    return {
      templates: [],
      selectedTemplateId: '',
      loadingTemplates: false,
      isProcessing: false,
      error: ''
    }
  },
  watch: {
    // Khi modal mở lên thì mới tải danh sách mẫu
    isOpen(newVal) {
      if (newVal) {
        this.fetchTemplates();
        this.selectedTemplateId = '';
        this.error = '';
      }
    }
  },
  methods: {
    close() {
      this.$emit('close');
    },
    async fetchTemplates() {
      this.loadingTemplates = true;
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/document-templates/');
        this.templates = response.data;
      } catch (e) {
        this.error = 'Không tải được danh sách mẫu.';
      } finally {
        this.loadingTemplates = false;
      }
    },
    async downloadDoc() {
      if (!this.selectedTemplateId) return;

      this.isProcessing = true;
      this.error = '';

      try {
        const url = `http://127.0.0.1:8000/api/loan-profiles/${this.profileId}/generate-document/`;

        // Gọi API với responseType là 'blob' để nhận file
        const response = await axios.post(
          url,
          { template_id: this.selectedTemplateId },
          { responseType: 'blob' }
        );

        // Tạo link ảo để trình duyệt tải file về
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);

        // Lấy tên file từ Header (nếu Backend có gửi) hoặc đặt tên mặc định
        const disposition = response.headers['content-disposition'];
        let filename = `HopDong_${this.profileId}.docx`;
        if (disposition && disposition.indexOf('filename=') !== -1) {
             const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
             if (matches != null && matches[1]) {
               filename = matches[1].replace(/['"]/g, '');
             }
        }

        link.download = filename;
        link.click();

        // Đóng modal sau khi tải xong
        this.close();

      } catch (e) {
        console.error(e);
        // Đọc lỗi từ Blob (vì responseType='blob' nên lỗi JSON cũng bị biến thành blob)
        if (e.response && e.response.data instanceof Blob) {
            const text = await e.response.data.text();
            this.error = 'Lỗi Server: ' + text;
        } else {
            this.error = 'Có lỗi xảy ra khi sinh hợp đồng.';
        }
      } finally {
        this.isProcessing = false;
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 20px; border-radius: 8px; width: 400px; max-width: 90%; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
.modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
.modal-header h3 { margin: 0; color: #2c3e50; }
.close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #888; }
.template-select { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; margin-bottom: 15px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; }
.btn-cancel { background: #95a5a6; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
.btn-download { background: #e67e22; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
.btn-download:disabled { background: #f39c12; opacity: 0.7; cursor: not-allowed; }
.error-msg { color: red; margin-bottom: 10px; font-size: 0.9rem; }
</style>
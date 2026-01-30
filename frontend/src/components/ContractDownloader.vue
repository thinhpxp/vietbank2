<template>
  <div v-if="isOpen" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Xuất Hợp đồng</h3>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="modal-body">
        <p>Chọn các mẫu hợp đồng muốn xuất cho hồ sơ: <strong>{{ profileName }}</strong></p>

        <div v-if="loadingTemplates">Đang tải danh sách mẫu...</div>

        <div v-else class="template-table-container">
          <table class="template-table">
            <thead>
              <tr>
                <th style="width: 40px;"><input type="checkbox" @change="toggleAll" :checked="isAllSelected"></th>
                <th>Tên mẫu</th>
                <th>Bộ phận</th>
                <th>Ghi chú</th>
                <th style="width: 80px;">Tải về</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tpl in templates" :key="tpl.id">
                <td><input type="checkbox" v-model="selectedTemplateIds" :value="tpl.id"></td>
                <td>{{ tpl.name }}</td>
                <td><span class="dept-badge" v-if="tpl.department">{{ tpl.department }}</span></td>
                <td class="cell-note">{{ tpl.description }}</td>
                <td>
                  <button class="btn-icon" title="Tải nhanh bản .docx" @click="downloadIndividual(tpl.id)">
                    📥
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="close">Hủy</button>
        <button class="btn-download" @click="downloadBulk" :disabled="selectedTemplateIds.length === 0 || isProcessing">
          {{ isProcessing ? 'Đang xử lý...' : 'Tải các mẫu đã chọn (.zip)' }}
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
      selectedTemplateIds: [], // Mảng chứa ID các mẫu được chọn
      loadingTemplates: false,
      isProcessing: false,
      error: ''
    }
  },
  computed: {
    isAllSelected() {
      return this.templates.length > 0 && this.selectedTemplateIds.length === this.templates.length;
    }
  },
  watch: {
    // Khi modal mở lên thì mới tải danh sách mẫu
    isOpen(newVal) {
      if (newVal) {
        this.fetchTemplates();
        this.selectedTemplateIds = [];
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
    toggleAll(e) {
      if (e.target.checked) {
        this.selectedTemplateIds = this.templates.map(t => t.id);
      } else {
        this.selectedTemplateIds = [];
      }
    },
    async downloadIndividual(tplId) {
      await this.executeDownload({ template_id: tplId });
    },
    async downloadBulk() {
      if (this.selectedTemplateIds.length === 0) return;
      await this.executeDownload({ template_ids: this.selectedTemplateIds });
    },
    async executeDownload(payload) {
      this.isProcessing = true;
      this.error = '';

      try {
        const url = `http://127.0.0.1:8000/api/loan-profiles/${this.profileId}/generate-document/`;
        const response = await axios.post(url, payload, { responseType: 'blob' });

        const contentType = response.headers['content-type'];
        const isZip = contentType && contentType.includes('application/zip');
        const blob = new Blob([response.data], { type: contentType });

        const disposition = response.headers['content-disposition'];
        let filename = isZip ? `${this.profileName}.zip` : `HopDong_${this.profileId}.docx`;

        if (disposition && disposition.indexOf('filename=') !== -1) {
          const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
          if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
          }
        }

        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        link.click();
      } catch (e) {
        console.error(e);
        if (e.response && e.response.data instanceof Blob) {
          const text = await e.response.data.text();
          this.error = 'Lỗi Server: ' + text;
        } else {
          this.error = 'Có lỗi xảy ra khi tải tài liệu.';
        }
      } finally {
        this.isProcessing = false;
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 700px;
  max-width: 95%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #888;
}

.template-table-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 15px;
}

.template-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.template-table th,
.template-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  text-align: left;
}

.template-table th {
  background: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 1;
}

.template-table tr:hover {
  background: #fafafa;
}

.dept-badge {
  background: #e8f4fd;
  color: #2980b9;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.cell-note {
  color: #666;
  font-style: italic;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0 5px;
  transition: transform 0.2s;
}

.btn-icon:hover {
  transform: scale(1.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-download {
  background: #e67e22;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.btn-download:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.error-msg {
  color: #e74c3c;
  margin-top: 10px;
  font-size: 0.9rem;
  font-weight: 500;
}
</style>
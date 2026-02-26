<template>
  <BaseModal :isOpen="isOpen" :title="'Xuất Hợp đồng: ' + profileName" :initialWidth="800" :isResizable="true"
    @close="close">
    <div class="downloader-content">
      <p class="text-muted mb-4">Chọn các mẫu hợp đồng muốn xuất cho hồ sơ.</p>

      <div class="filter-bar mb-4" v-if="!loadingTemplates && templates.length > 1">
        <div class="filter-group">
          <label>Tìm kiếm:</label>
          <input v-model="filters.search" placeholder="Tìm theo tên mẫu hoặc bộ phận..." class="modal-search-input"
            style="width: 250px">
        </div>
      </div>

      <div v-if="loadingTemplates" class="loading-text">Đang tải danh sách mẫu...</div>

      <div v-else class="data-table-vxe">
        <vxe-table border round :data="sortedTemplates" :row-config="{ isHover: true }"
          :column-config="{ resizable: true }" :sort-config="{ trigger: 'cell' }"
          @checkbox-change="handleCheckboxChange" @checkbox-all="handleCheckboxAll" ref="vxeTable" height="auto"
          class="downloader-table">

          <vxe-column type="checkbox" width="50"></vxe-column>

          <vxe-column field="name" title="Tên mẫu" min-width="200" sortable></vxe-column>

          <vxe-column field="department" title="Bộ phận" width="150" sortable>
            <template #default="{ row }">
              <span class="status-badge draft" v-if="row.department">{{ row.department }}</span>
            </template>
          </vxe-column>

          <vxe-column field="description" title="Ghi chú" min-width="200">
            <template #default="{ row }">
              <div class="cell-note">{{ row.description }}</div>
            </template>
          </vxe-column>

          <vxe-column field="loop_object_type" title="Tách riêng" width="100" align="center">
            <template #default="{ row }">
              <input v-if="row.loop_object_type" type="checkbox" v-model="batchTemplateIds" :value="row.id"
                title="Tách riêng từng file">
              <span v-else class="text-muted">—</span>
            </template>
          </vxe-column>

          <vxe-column title="Tải về" width="80" align="center" fixed="right">
            <template #default="{ row }">
              <button class="btn-action btn-doc btn-icon-sm" title="Tải nhanh bản .docx"
                @click="downloadIndividual(row.id)" :disabled="isProcessing">
                <SvgIcon name="download" size="sm" />
              </button>
            </template>
          </vxe-column>
        </vxe-table>
      </div>

      <div v-if="batchProgress" class="batch-progress">
        <span class="spinner">⏳</span> {{ batchProgress }}
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>
    </div>

    <template #footer>
      <button class="btn-action btn-cancel" @click="close">Hủy</button>
      <button class="btn-action btn-download" @click="downloadBulk"
        :disabled="selectedTemplateIds.length === 0 || isProcessing">
        <SvgIcon name="download" size="sm" v-if="!isProcessing" />
        {{ isProcessing ? 'Đang xử lý...' : 'Tải các mẫu đã chọn' }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import BaseModal from '@/components/BaseModal.vue';
import SvgIcon from '@/components/common/SvgIcon.vue';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'ContractDownloader',
  components: {
    BaseModal,
    SvgIcon
  },
  mixins: [FilterableTableMixin],
  props: {
    isOpen: Boolean,
    profileId: Number,
    profileName: String
  },
  emits: ['close'],
  data() {
    return {
      templates: [],
      selectedTemplateIds: [],
      batchTemplateIds: [],
      loadingTemplates: false,
      isProcessing: false,
      batchProgress: '',
      error: '',
      filters: { search: '' }
    }
  },
  computed: {
    filteredTemplates() {
      return this.filterArray(this.templates, this.filters, {
        search: { type: 'text', fields: ['name', 'department'] }
      });
    },
    sortedTemplates() {
      return this.sortArray(this.filteredTemplates);
    },
    isAllSelected() {
      return this.sortedTemplates.length > 0 &&
        this.sortedTemplates.every(t => this.selectedTemplateIds.includes(t.id));
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        this.fetchTemplates();
        this.selectedTemplateIds = [];
        this.batchTemplateIds = [];
        this.batchProgress = '';
        this.error = '';
        this.filters.search = '';
      }
    },
  },
  methods: {
    close() {
      this.$emit('close');
    },
    async fetchTemplates() {
      this.loadingTemplates = true;
      try {
        const response = await axios.get(`${API_URL}/document-templates/`);
        this.templates = response.data;
      } catch (e) {
        this.error = 'Không tải được danh sách mẫu.';
      } finally {
        this.loadingTemplates = false;
      }
    },
    handleCheckboxChange({ checked, row }) {
      if (checked) {
        if (!this.selectedTemplateIds.includes(row.id)) this.selectedTemplateIds.push(row.id);
      } else {
        this.selectedTemplateIds = this.selectedTemplateIds.filter(id => id !== row.id);
      }
    },
    handleCheckboxAll({ checked }) {
      if (checked) {
        this.selectedTemplateIds = this.sortedTemplates.map(t => t.id);
      } else {
        this.selectedTemplateIds = [];
      }
    },

    async downloadIndividual(tplId) {
      this.isProcessing = true;
      this.error = '';
      try {
        const isBatch = this.batchTemplateIds.map(Number).includes(Number(tplId));
        if (isBatch) {
          await this.executeFrontendBatch(Number(tplId));
        } else {
          const payload = {
            template_id: Number(tplId),
            batch_template_ids: []
          };
          await this.executeDownload(payload);
        }
      } finally {
        this.isProcessing = false;
        this.batchProgress = '';
      }
    },

    async executeFrontendBatch(templateId) {
      try {
        const url = `${API_URL}/loan-profiles/${this.profileId}/generate-document/`;
        const metaResp = await axios.post(url, {
          template_id: templateId,
          batch_template_ids: [templateId],
          return_metadata: true
        });

        const objects = metaResp.data.objects || [];
        if (objects.length === 0) {
          this.error = `Không tìm thấy đối tượng nào để tách cho mẫu "${this.getTemplateName(templateId)}".`;
          return;
        }

        for (let i = 0; i < objects.length; i++) {
          const obj = objects[i];
          this.batchProgress = `Đang tải file ${i + 1}/${objects.length} — ${this.getTemplateName(templateId)}`;

          const response = await axios.post(url, {
            template_id: templateId,
            export_mode: 'BATCH',
            target_object_id: obj.id
          }, { responseType: 'blob' });

          const contentType = response.headers['content-type'] || 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
          const blob = new Blob([response.data], { type: contentType });

          const disposition = response.headers['content-disposition'];
          let filename = `TachRieng_${obj.identity}.docx`;

          if (disposition && disposition.indexOf('filename=') !== -1) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
            if (matches != null && matches[1]) {
              filename = decodeURIComponent(matches[1].replace(/['"]/g, ''));
            }
          }

          this.triggerDownload(blob, filename);
          await new Promise(r => setTimeout(r, 800));
        }
      } catch (e) {
        console.error('Frontend Batch error:', e);
        this.error = 'Có lỗi xảy ra khi tải tách rời tài liệu.';
      }
    },

    async downloadBulk() {
      if (this.selectedTemplateIds.length === 0) return;

      this.isProcessing = true;
      this.error = '';
      this.batchProgress = 'Đang chuẩn bị tài liệu...';
      try {
        const payload = {
          template_ids: this.selectedTemplateIds.map(Number),
          batch_template_ids: this.batchTemplateIds.map(Number)
        };
        await this.executeDownload(payload);
      } finally {
        this.isProcessing = false;
        this.batchProgress = '';
      }
    },

    async executeDownload(payload) {
      this.error = '';
      try {
        const url = `${API_URL}/loan-profiles/${this.profileId}/generate-document/`;
        const response = await axios.post(url, payload, { responseType: 'blob' });

        const contentType = response.headers['content-type'];
        const isZip = contentType && contentType.includes('application/zip');
        const blob = new Blob([response.data], { type: contentType });

        const disposition = response.headers['content-disposition'];
        let filename = isZip ? `${this.profileName}.zip` : `HopDong_${this.profileId}.docx`;

        if (disposition && disposition.indexOf('filename=') !== -1) {
          const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
          if (matches != null && matches[1]) {
            filename = decodeURIComponent(matches[1].replace(/['"]/g, ''));
          }
        }

        this.triggerDownload(blob, filename);
      } catch (e) {
        console.error(e);
        if (e.response && e.response.data instanceof Blob) {
          const text = await e.response.data.text();
          this.error = 'Lỗi Server: ' + text;
        } else {
          this.error = 'Có lỗi xảy ra khi tải tài liệu.';
        }
      }
    },

    triggerDownload(blob, filename) {
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      setTimeout(() => {
        window.URL.revokeObjectURL(link.href);
      }, 1000);
    },

    getTemplateName(templateId) {
      const tpl = this.templates.find(t => t.id === templateId);
      return tpl ? tpl.name : `#${templateId}`;
    }
  }
}
</script>

<style scoped>
.downloader-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding-bottom: var(--spacing-md);
}

.modal-search-input {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 6px 12px;
  font-size: 14px;
}

.modal-search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.data-table-vxe {
  flex: 1;
  min-height: 200px;
}

.cell-note {
  color: var(--color-text-muted);
  font-style: italic;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-center {
  text-align: center;
}

.btn-icon-sm {
  min-width: auto;
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: var(--radius-full);
}

.btn-download {
  background-color: var(--color-primary);
  color: white;
}

.loading-text {
  color: var(--color-text-muted);
  padding: var(--spacing-xl) 0;
  text-align: center;
}

.batch-progress {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--slate-50);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  color: var(--color-primary);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.error-msg {
  color: var(--color-danger);
  margin-top: var(--spacing-md);
  font-size: var(--font-sm);
  font-weight: 500;
}

.spinner {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
</style>
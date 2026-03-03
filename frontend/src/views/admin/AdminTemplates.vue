<template>
  <div class="admin-page">
    <h2>Quản lý Mẫu Hợp đồng</h2>
    <div class="admin-panel mb-6">
      <h4>Tải lên mẫu mới</h4>
      <div class="admin-row mb-2">
        <input class="admin-input" type="text" v-model="newName" placeholder="Tên hiển thị (*)">
        <input class="admin-input" type="text" v-model="newDept" placeholder="Bộ phận (VD: Tín dụng)">
        <input class="admin-input" type="text" v-model="newDesc" placeholder="Ghi chú mẫu này">
      </div>

      <div class="admin-row items-center">
        <select class="admin-select" v-model="newLoopObjectType"
          title="Loại đối tượng lặp (cho tính năng Tách riêng file)">
          <option :value="null">-- Không lặp --</option>
          <option v-for="ot in objectTypes" :key="ot.id" :value="ot.id">
            Loại lặp: {{ ot.name }}
          </option>
        </select>

        <div class="admin-file-upload">
          <label for="template-file" class="btn-action btn-secondary whitespace-nowrap"
            title="Chọn tệp DOCX từ máy tính">
            <SvgIcon name="folder" size="sm" />
            <span>{{ selectedFile ? 'Chọn lại' : 'Chọn tệp (.docx)' }}</span>
          </label>
          <input id="template-file" class="admin-hidden-input" type="file" ref="fileInput" @change="handleFileChange">
          <span v-if="selectedFile" class="admin-file-name" :title="selectedFile.name">{{ selectedFile.name }}</span>
        </div>

        <button @click="uploadTemplate" class="btn-action btn-success btn-icon-only" title="Tải lên Mẫu Hợp đồng">
          <SvgIcon name="upload" size="sm" />
        </button>
      </div>
    </div>

    <div class="filter-bar mb-4">
      <div class="filter-group">
        <label>Tìm kiếm:</label>
        <input v-model="filters.search" placeholder="Tìm theo tên mẫu hoặc bộ phận..." class="admin-form-control"
          style="width: 300px">
      </div>
    </div>

    <div class="data-table-vxe">
      <vxe-table border round :data="filteredTemplates" :row-config="{ isHover: true }"
        :column-config="{ resizable: true }"
        :sort-config="{ trigger: 'cell', defaultSort: { field: 'id', order: 'desc' } }">
        <vxe-column field="id" title="ID" width="60" sortable></vxe-column>
        <vxe-column field="name" title="Tên Mẫu" min-width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.name" class="vxe-input-minimal">
            <span v-else>{{ row.name }}</span>
          </template>
        </vxe-column>
        <vxe-column field="department" title="Bộ phận" width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.department" class="vxe-input-minimal">
            <span v-else>{{ row.department }}</span>
          </template>
        </vxe-column>
        <vxe-column field="description" title="Ghi chú" min-width="150">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.description" class="vxe-input-minimal">
            <span v-else>{{ row.description }}</span>
          </template>
        </vxe-column>
        <vxe-column field="loop_object_type" title="Lặp theo" width="150">
          <template #default="{ row }">
            <select v-if="editingId === row.id" v-model="row.loop_object_type" class="vxe-input-minimal">
              <option :value="null">-- Không --</option>
              <option v-for="ot in objectTypes" :key="ot.id" :value="ot.id">
                {{ ot.name }}
              </option>
            </select>
            <span v-else>{{ row.loop_object_type_name || '—' }}</span>
          </template>
        </vxe-column>
        <vxe-column field="uploaded_at" title="Thời điểm" width="160" sortable>
          <template #default="{ row }">
            {{ formatDate(row.uploaded_at) }}
          </template>
        </vxe-column>
        <vxe-column title="Hành động" width="220" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <button v-if="editingId === row.id" @click="updateTemplate(row)" class="btn-action btn-save btn-icon-only"
                title="Lưu thay đổi">
                <SvgIcon name="save" size="sm" />
              </button>
              <button v-else @click="editingId = row.id" class="btn-action btn-edit btn-icon-only" title="Sửa">
                <SvgIcon name="edit" size="sm" />
              </button>
              <a :href="row.file" target="_blank" class="btn-action btn-doc btn-icon-only no-underline"
                title="Tải mẫu về máy">
                <SvgIcon name="download" size="sm" />
              </a>
              <button @click="deleteTemplate(row.id)" class="btn-action btn-delete btn-icon-only" title="Xóa">
                <SvgIcon name="trash" size="sm" />
              </button>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa mẫu '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />

    <ConfirmModal :visible="showErrorModal" type="error" mode="alert" :title="errorModalTitle"
      :message="errorModalMessage" :errorCode="errorModalCode" :details="errorModalDetails" :showTimestamp="true"
      confirmText="Đóng" @confirm="showErrorModal = false" @cancel="showErrorModal = false" />
    <ConfirmModal :visible="showSuccessModal" type="success" mode="alert" :title="successModalTitle"
      :message="successModalMessage" confirmText="OK" @confirm="showSuccessModal = false"
      @cancel="showSuccessModal = false" />
    <ConfirmModal :visible="showWarningModal" type="warning" mode="alert" :title="warningModalTitle"
      :message="warningModalMessage" confirmText="Đóng" @confirm="showWarningModal = false"
      @cancel="showWarningModal = false" />
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  components: { ConfirmModal },
  mixins: [errorHandlingMixin, FilterableTableMixin],
  data() {
    return {
      templates: [],
      objectTypes: [],  // MỚI: Danh sách loại đối tượng
      newName: '',
      newDept: '',
      newDesc: '',
      newLoopObjectType: null,  // MỚI: Loại đối tượng lặp khi upload
      selectedFile: null,
      editingId: null,
      filters: { search: '' },
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: ''
    }
  },
  computed: {
    filteredTemplates() {
      return this.filterArray(this.templates, this.filters, {
        search: { type: 'text', fields: ['name', 'department'] }
      });
    }
  },
  watch: {
  },
  mounted() {
    this.fetchTemplates();
    this.fetchObjectTypes();
  },
  methods: {
    async fetchTemplates() {
      try {
        const res = await axios.get(`${API_URL}/document-templates/`);
        this.templates = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách mẫu');
      }
    },
    // MỚI: Fetch danh sách loại đối tượng
    async fetchObjectTypes() {
      try {
        const res = await axios.get(`${API_URL}/object-types/`);
        this.objectTypes = res.data;
      } catch (e) {
        console.error('Failed to fetch object types:', e);
      }
    },
    handleFileChange(e) {
      this.selectedFile = e.target.files[0];
    },
    async uploadTemplate() {
      if (!this.selectedFile || !this.newName) {
        this.showWarning('Vui lòng nhập tên và chọn file!', 'Thiếu thông tin');
        return;
      }

      const formData = new FormData();
      formData.append('name', this.newName);
      formData.append('department', this.newDept);
      formData.append('description', this.newDesc);
      formData.append('file', this.selectedFile);
      if (this.newLoopObjectType) {
        formData.append('loop_object_type', this.newLoopObjectType);  // MỚI
      }

      try {
        await axios.post(`${API_URL}/document-templates/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        this.newName = ''; this.newDept = ''; this.newDesc = ''; this.newLoopObjectType = null; this.selectedFile = null; this.$refs.fileInput.value = '';
        this.fetchTemplates();
        this.$toast.success('Upload mẫu tài liệu mới thành công!');
      } catch (e) {
        this.showError(e, 'Lỗi upload');
      }
    },
    deleteTemplate(id) {
      const tpl = this.templates.find(t => t.id === id);
      this.deleteTargetId = id;
      this.deleteTargetName = tpl ? tpl.name : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        try {
          await axios.delete(`${API_URL}/document-templates/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchTemplates();
          this.$toast.success('Đã xóa mẫu thành công!');
        } catch (e) {
          this.showDeleteModal = false;
          this.showError(e, 'Lỗi xóa mẫu');
        }
      }
    },
    async updateTemplate(tpl) {
      try {
        await axios.patch(`${API_URL}/document-templates/${tpl.id}/`, {
          name: tpl.name,
          department: tpl.department,
          description: tpl.description,
          loop_object_type: tpl.loop_object_type  // MỚI
        });
        this.editingId = null;
        this.$toast.success('Cập nhật thông tin mẫu thành công!');
        this.fetchTemplates();
      } catch (e) {
        this.showError(e, 'Lỗi khi cập nhật');
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString('vi-VN');
    }
  }
}
</script>
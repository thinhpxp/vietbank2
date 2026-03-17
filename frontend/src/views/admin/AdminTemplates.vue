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

        <button @click="uploadTemplate" class="btn-action btn-create btn-icon-only" title="Tải lên Mẫu Hợp đồng">
          <SvgIcon name="upload" size="sm" />
        </button>
      </div>
    </div>

    <div class="filter-bar admin-row align-end gap-md mb-4">
      <div class="filter-group" style="flex: 1; min-width: 300px;">
        <label class="premium-label">
          <SvgIcon name="search" size="xs" /> Tìm kiếm
        </label>
        <div class="premium-input-wrapper">
          <input v-model="filters.search" placeholder="Tìm theo tên mẫu hoặc bộ phận..."
            class="filter-control premium-input">
        </div>
      </div>

      <div class="filter-group" style="flex: 0 0 auto;">
        <label class="premium-label" style="visibility: hidden;">&nbsp;</label>
        <div class="premium-input-wrapper">
          <button class="btn-action btn-secondary flex items-center gap-2" @click="resetFilters" title="Đặt lại bộ lọc">
            <SvgIcon name="x" size="sm" /> <span>Đặt lại</span>
          </button>
        </div>
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
              <template v-if="editingId === row.id">
                <button @click="updateTemplate(row)" class="btn-action btn-save btn-icon-only" title="Lưu thay đổi">
                  <SvgIcon name="save" size="sm" />
                </button>
                <button @click="editingId = null" class="btn-action btn-secondary btn-icon-only" title="Hủy bỏ">
                  <SvgIcon name="x" size="sm" />
                </button>
              </template>
              <template v-else>
                <button @click="editingId = row.id" class="btn-action btn-edit btn-icon-only" :disabled="!canChange"
                  :title="canChange ? 'Sửa' : 'Không có quyền sửa'">
                  <SvgIcon name="edit" size="sm" />
                </button>
                <a :href="row.file" target="_blank" class="btn-action btn-download btn-icon-only no-underline"
                  title="Tải mẫu về máy">
                  <SvgIcon name="download" size="sm" />
                </a>
                <button @click="deleteTemplate(row.id)" class="btn-action btn-delete btn-icon-only"
                  :disabled="!canDelete" :title="canDelete ? 'Xóa' : 'Không có quyền xóa'">
                  <SvgIcon name="trash" size="sm" />
                </button>
              </template>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa mẫu '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />

  </div>
</template>

<script>
import MasterService from '@/services/master.service';
import { useAuthStore } from '@/store/auth.store';
import SvgIcon from '@/components/common/SvgIcon.vue';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'AdminTemplates',
  title: 'Quản lý Mẫu Hợp đồng',
  components: { ConfirmModal, SvgIcon },
  mixins: [errorHandlingMixin, FilterableTableMixin],
  data() {
    return {
      templates: [],
      objectTypes: [],
      newName: '',
      newDept: '',
      newDesc: '',
      newLoopObjectType: null,
      selectedFile: null,
      editingId: null,
      filters: { search: '' },
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: '',
      authStore: useAuthStore()
    }
  },
  computed: {
    filteredTemplates() {
      return this.filterArray(this.templates, this.filters, {
        search: { type: 'text', fields: ['name', 'department'] }
      });
    },
    canCreate() { return this.authStore.hasPermission('document_automation.add_documenttemplate'); },
    canChange() { return this.authStore.hasPermission('document_automation.change_documenttemplate'); },
    canDelete() { return this.authStore.hasPermission('document_automation.delete_documenttemplate'); },
  },
  mounted() {
    this.fetchTemplates();
    this.fetchObjectTypes();
  },
  methods: {
    async fetchTemplates() {
      try {
        const res = await MasterService.getTemplates();
        this.templates = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách mẫu');
      }
    },
    async fetchObjectTypes() {
      try {
        const res = await MasterService.getObjectTypes();
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
        formData.append('loop_object_type', this.newLoopObjectType);
      }

      try {
        await MasterService.createTemplate(formData);
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
          await MasterService.deleteTemplate(this.deleteTargetId);
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
        await MasterService.updateTemplate(tpl.id, {
          name: tpl.name,
          department: tpl.department,
          description: tpl.description,
          loop_object_type: tpl.loop_object_type
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
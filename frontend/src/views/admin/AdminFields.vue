<template>
  <div class="admin-page">
    <h2>Quản lý Trường Dữ liệu</h2>

    <!-- Form thêm mới -->
    <div class="admin-panel">
      <h4>Thêm trường mới</h4>
      <div class="admin-row mb-2">
        <input v-model="newField.label" placeholder="Nhãn hiển thị (VD: Số tiền)" class="admin-input">
        <input v-model="newField.placeholder_key" placeholder="Key (VD: so_tien)" class="admin-input">
        <input v-model="newField.note" placeholder="Ghi chú về trường thông tin này" class="admin-input">
      </div>
      <div class="admin-row mb-2">
        <input v-model.number="newField.order" type="text" inputmode="numeric" placeholder="Thứ tự"
          style="max-width: 80px" class="admin-input">
        <input v-model.number="newField.width_cols" type="text" inputmode="numeric" min="1" max="12"
          placeholder="Độ rộng (1-12)" style="max-width: 100px" class="admin-input">
        <input v-model="newField.css_class" placeholder="CSS Class (VD: text-red)" class="admin-input">
        <input v-model="newField.default_value" placeholder="Giá trị mặc định" class="admin-input">
      </div>
      <div class="admin-row">
        <select v-model="newField.data_type" class="admin-input">
          <option value="TEXT">Văn bản</option>
          <option value="TEXTAREA">Đoạn văn bản</option>
          <option value="NUMBER">Số</option>
          <option value="DATE">Ngày</option>
          <option value="CHECKBOX">Hộp kiểm</option>
        </select>
        <label class="admin-checkbox-label">
          <input type="checkbox" v-model="newField.use_digit_grouping"> Tách nghìn
        </label>
        <label class="admin-checkbox-label">
          <input type="checkbox" v-model="newField.show_amount_in_words"> Hiện chữ
        </label>
        <select v-model="newField.group" class="admin-input">
          <option :value="null">-- Chọn nhóm --</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
        <button @click="addField" class="btn-action btn-create btn-icon-only" :disabled="!canCreate"
          :title="canCreate ? 'Thêm trường dữ liệu mới' : 'Không có quyền tạo'">
          <SvgIcon name="plus" size="sm" />
        </button>
      </div>
    </div>

    <!-- Bộ lọc (Premium Refactor) -->
    <div class="filter-bar admin-row align-end gap-md mt-6">
      <div class="filter-group search-container" style="flex: 1.5; min-width: 250px;">
        <label class="premium-label">
          <SvgIcon name="search" size="xs" /> Tìm kiếm
        </label>
        <div class="premium-input-wrapper">
          <input v-model="filters.search" placeholder="Nhãn hoặc Key..." class="filter-control premium-input">
        </div>
      </div>

      <div class="filter-group" style="flex: 1; min-width: 180px;">
        <label class="premium-label">
          <SvgIcon name="folder" size="xs" /> Nhóm
        </label>
        <select v-model="filters.group" class="filter-control premium-select">
          <option :value="null">-- Tất cả nhóm --</option>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>

      <div class="filter-group" style="flex: 1; min-width: 150px;">
        <label class="premium-label">
          <SvgIcon name="file" size="xs" /> Loại dữ liệu
        </label>
        <select v-model="filters.dataType" class="filter-control premium-select">
          <option :value="null">-- Tất cả loại --</option>
          <option value="TEXT">Văn bản</option>
          <option value="TEXTAREA">Đoạn văn bản</option>
          <option value="NUMBER">Số</option>
          <option value="DATE">Ngày</option>
          <option value="CHECKBOX">Hộp kiểm</option>
        </select>
      </div>

      <div class="filter-group" style="flex: 1; min-width: 180px;">
        <label class="premium-label">
          <SvgIcon name="shield" size="xs" /> Loại đối tượng
        </label>
        <select v-model="filters.objectType" class="filter-control premium-select">
          <option :value="null">-- Tất cả đối tượng --</option>
          <option v-for="t in objectTypes" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
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

    <!-- Danh sách -->
    <div class="data-table-vxe">
      <vxe-table border round :data="filteredFields" :row-config="{ isHover: true }"
        :column-config="{ resizable: true }"
        :sort-config="{ trigger: 'cell', defaultSort: { field: 'id', order: 'desc' } }">

        <vxe-column field="id" title="ID" width="60" sortable></vxe-column>

        <vxe-column field="order" title="Thứ tự" width="80" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model.number="row.order" type="text" inputmode="numeric"
              class="vxe-input-minimal">
            <span v-else>{{ row.order }}</span>
          </template>
        </vxe-column>

        <vxe-column field="placeholder_key" title="Key" width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.placeholder_key" class="vxe-input-minimal">
            <code v-else>{{ row.placeholder_key }}</code>
          </template>
        </vxe-column>

        <vxe-column field="label" title="Nhãn" min-width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.label" class="vxe-input-minimal">
            <span v-else>{{ row.label }}</span>
          </template>
        </vxe-column>

        <vxe-column field="data_type" title="Loại" width="120" sortable>
          <template #default="{ row }">
            <select v-if="editingId === row.id" v-model="row.data_type" class="vxe-input-minimal">
              <option value="TEXT">Văn bản</option>
              <option value="TEXTAREA">Đoạn văn bản</option>
              <option value="NUMBER">Số</option>
              <option value="DATE">Ngày</option>
              <option value="CHECKBOX">Hộp kiểm</option>
            </select>
            <span v-else>{{ row.data_type }}</span>
          </template>
        </vxe-column>

        <vxe-column field="is_system" title="Hệ thống" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.is_system" class="admin-badge badge-admin">System</span>
            <span v-else class="admin-badge badge-inactive">Custom</span>
          </template>
        </vxe-column>

        <vxe-column field="group_name" title="Nhóm" width="150" sortable>
          <template #default="{ row }">
            <select v-if="editingId === row.id" v-model="row.group" class="vxe-input-minimal">
              <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
            </select>
            <span v-else>{{ row.group_name }}</span>
          </template>
        </vxe-column>

        <vxe-column field="width_cols" title="Rộng" width="70">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model.number="row.width_cols" type="text" inputmode="numeric"
              class="vxe-input-minimal">
            <span v-else>{{ row.width_cols }}</span>
          </template>
        </vxe-column>

        <vxe-column field="css_class" title="CSS" width="100">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.css_class" class="vxe-input-minimal">
            <span v-else>{{ row.css_class }}</span>
          </template>
        </vxe-column>

        <vxe-column field="default_value" title="Mặc định" min-width="120">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.default_value" class="vxe-input-minimal"
              placeholder="=SUM(...) hoặc {{ key }}">
            <span v-else>
              <span v-if="row.default_value && row.default_value.trim().startsWith('=')" class="badge-computed-admin"
                title="Computed Field">⚡</span>
              <span v-else-if="row.default_value && row.default_value.includes('{{')" class="badge-template-admin"
                title="Text Template">🔗</span>
              {{ row.default_value }}
            </span>
          </template>
        </vxe-column>

        <vxe-column field="use_digit_grouping" title="Tách nghìn" width="100" align="center">
          <template #default="{ row }">
            <input v-if="editingId === row.id" type="checkbox" v-model="row.use_digit_grouping">
            <span v-else>{{ row.use_digit_grouping ? '✅' : '❌' }}</span>
          </template>
        </vxe-column>

        <vxe-column field="show_amount_in_words" title="Hiện chữ" width="100" align="center">
          <template #default="{ row }">
            <input v-if="editingId === row.id" type="checkbox" v-model="row.show_amount_in_words">
            <span v-else>{{ row.show_amount_in_words ? '✅' : '❌' }}</span>
          </template>
        </vxe-column>

        <vxe-column title="Form" width="180">
          <template #default="{ row }">
            <div v-if="editingId === row.id">
              <div v-for="form in allForms" :key="form.id">
                <label class="admin-checkbox-label">
                  <input type="checkbox" :value="form.id" v-model="row.allowed_forms">
                  {{ form.name }}
                </label>
              </div>
            </div>
            <div v-else>
              <div class="flex flex-col gap-1 items-start">
                <span v-for="fid in row.allowed_forms.slice(0, 2)" :key="fid" class="badge badge-inactive">
                  {{allForms.find(f => f.id === fid)?.name || fid}}
                </span>
                <span v-if="row.allowed_forms.length > 2" class="badge badge-inactive" style="opacity: 0.7"
                  :title="row.allowed_forms.map(fid => allForms.find(f => f.id === fid)?.name || fid).join(', ')">
                  +{{ row.allowed_forms.length - 2 }} more...
                </span>
              </div>
            </div>
          </template>
        </vxe-column>

        <vxe-column title="Loại đối tượng" width="200">
          <template #default="{ row }">
            <div v-if="editingId === row.id">
              <div v-for="type in objectTypes" :key="type.id">
                <label class="admin-checkbox-label">
                  <input type="checkbox" :value="type.id" v-model="row.allowed_object_types">
                  {{ type.name }}
                </label>
              </div>
            </div>
            <div v-else>
              <div class="flex flex-col gap-1 items-start">
                <span v-for="tid in row.allowed_object_types.slice(0, 2)" :key="tid" class="badge badge-inactive">
                  {{objectTypes.find(t => t.id === tid)?.name || tid}}
                </span>
                <span v-if="row.allowed_object_types.length > 2" class="badge badge-inactive" style="opacity: 0.7"
                  :title="row.allowed_object_types.map(tid => objectTypes.find(t => t.id === tid)?.name || tid).join(', ')">
                  +{{ row.allowed_object_types.length - 2 }} more...
                </span>
              </div>
            </div>
          </template>
        </vxe-column>

        <vxe-column title="Hành động" width="220" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <template v-if="editingId === row.id">
                <button @click="updateField(row)" class="btn-action btn-save btn-icon-only" title="Lưu thay đổi">
                  <SvgIcon name="save" size="sm" />
                </button>
                <button @click="editingId = null" class="btn-action btn-secondary btn-icon-only" title="Hủy bỏ">
                  <SvgIcon name="x" size="sm" />
                </button>
              </template>
              <template v-else>
                <button @click="editingId = row.id" class="btn-action btn-edit btn-icon-only" :disabled="!canChange"
                  :title="canChange ? 'Chỉnh sửa' : 'Không có quyền sửa'">
                  <SvgIcon name="edit" size="sm" />
                </button>
                <button @click="copyField(row)" class="btn-action btn-copy btn-icon-only" :disabled="!canCreate"
                  :title="canCreate ? 'Sao chép' : 'Không có quyền tạo'">
                  <SvgIcon name="copy" size="sm" />
                </button>
                <button :disabled="row.is_system || !canDelete" @click="deleteField(row.id)"
                  class="btn-action btn-delete btn-icon-only"
                  :title="row.is_system ? 'Dữ liệu hệ thống, không thể xóa' : (canDelete ? 'Xóa' : 'Không có quyền xóa')">
                  <SvgIcon name="trash" size="sm" />
                </button>
              </template>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa trường '${deleteTargetLabel}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
    <!-- Generic Modals -->
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
import MasterService from '@/services/master.service';
import { useAuthStore } from '@/store/auth.store';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '../../mixins/FilterableTableMixin';
import SvgIcon from '../../components/common/SvgIcon.vue';

export default {
  name: 'AdminFields',
  title: 'Quản lý Trường dữ liệu',
  components: { ConfirmModal, SvgIcon },
  mixins: [errorHandlingMixin, FilterableTableMixin],
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
        order: null, width_cols: null, css_class: '', default_value: '', allowed_forms: [], allowed_object_types: [],
        use_digit_grouping: false, show_amount_in_words: false
      },
      allowed_object_types: [],
      authStore: useAuthStore()
    }
  },
  mounted() {
    this.fetchData();
    this.fetchForms();
  },
  computed: {
    filteredFields() {
      return this.filterArray(this.fields, this.filters, {
        search: { type: 'text', fields: ['label', 'placeholder_key'] },
        group: { type: 'exact' },
        dataType: { type: 'exact', field: 'data_type' },
        objectType: { type: 'array_includes', field: 'allowed_object_types' }
      });
    },
    canCreate() { return this.authStore.hasPermission('document_automation.add_field'); },
    canChange() { return this.authStore.hasPermission('document_automation.change_field'); },
    canDelete() { return this.authStore.hasPermission('document_automation.delete_field'); },
  },
  methods: {
    async fetchData() {
      try {
        const [resFields, resGroups, resTypes] = await Promise.all([
          MasterService.getFields(),
          MasterService.getGroups(),
          MasterService.getObjectTypes()
        ]);
        this.fields = resFields.data;
        this.groups = resGroups.data;
        this.objectTypes = resTypes.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải dữ liệu');
      }
    },
    async fetchForms() {
      try {
        const res = await MasterService.getFormViews();
        this.allForms = res.data;
      } catch (e) {
        this.showError(e, 'Lỗi tải danh sách Form');
      }
    },
    getFormNames(ids) {
      if (!ids || ids.length === 0) return 'Chưa gán (Ẩn)';
      return this.allForms
        .filter(f => ids.includes(f.id))
        .map(f => f.name)
        .join(', ');
    },
    async addField() {
      if (!this.newField.group) {
        this.showWarning('Vui lòng chọn nhóm!', 'Thiếu thông tin');
        return;
      }
      const isDuplicate = this.fields.some(f => f.placeholder_key === this.newField.placeholder_key);
      if (isDuplicate) {
        this.showWarning(`Key '${this.newField.placeholder_key}' đã tồn tại. Vui lòng chọn key khác để tránh xung đột dữ liệu.`, 'Trùng Key');
        return;
      }
      try {
        await MasterService.createField(this.newField);
        this.fetchData();
        this.newField = {
          label: '', placeholder_key: '', note: '', data_type: 'TEXT', group: this.newField.group,
          order: null, width_cols: null, css_class: '', use_digit_grouping: false, show_amount_in_words: false,
          allowed_object_types: [], allowed_forms: []
        };
        this.showSuccess('Thêm trường thành công!');
      } catch (e) {
        this.showError(e, 'Lỗi khi thêm trường');
      }
    },
    async updateField(field) {
      try {
        await MasterService.updateField(field.id, field);
        this.editingId = null;
        await this.fetchData();
      } catch (e) {
        this.showError(e, 'Lỗi khi cập nhật');
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
        try {
          await MasterService.deleteField(this.deleteTargetId);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchData();
          this.showSuccess('Đã xóa trường thành công!');
        } catch (e) {
          this.showDeleteModal = false;
          this.showError(e, 'Lỗi xóa trường');
        }
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

.badge-computed-admin,
.badge-template-admin {
  font-size: 0.85em;
  margin-right: 3px;
}

/* Premium Filter Bar Styles - Refactored to admin.css */
/* .btn-secondary - inherited from common-ui.css */
</style>
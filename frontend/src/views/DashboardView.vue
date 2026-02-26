<template>
  <div class="dashboard-container page-container">
    <div class="header-actions">
      <h2>Danh sách Hồ sơ Vay</h2>
      <button v-if="auth.hasPermission('document_automation.add_loanprofile')" class="btn-action btn-create"
        @click="openFormSelectModal">
        <SvgIcon name="plus" size="sm" /> <span>Tạo Mới</span>
      </button>
    </div>

    <!-- Filter Bar (Premium Refactor) -->
    <div class="filter-bar admin-row align-end gap-md mb-6">
      <div class="filter-group" style="flex: 1.5; min-width: 100px;">
        <label class="premium-label">
          <SvgIcon name="search" size="xs" /> Tìm kiếm
        </label>
        <div class="premium-input-wrapper">
          <input v-model="filters.search" placeholder="Tìm kiếm hồ sơ..." class="filter-control premium-input">
        </div>
      </div>

      <div class="filter-group" style="flex: 1; min-width: 180px;">
        <label class="premium-label">
          <SvgIcon name="shield" size="xs" /> Trạng thái
        </label>
        <select v-model="filters.status" class="filter-control premium-select">
          <option :value="null">- Tất cả trạng thái -</option>
          <option value="DRAFT">Nháp</option>
          <option value="FINALIZED">Đã khóa</option>
        </select>
      </div>

      <div class="filter-group" style="flex: 1; min-width: 150px;">
        <label class="premium-label">
          <SvgIcon name="calendar" size="xs" /> Ngày tạo
        </label>
        <input v-model="filters.createdDate" type="date" class="filter-control premium-input">
      </div>

      <div class="filter-group" style="flex: 1; min-width: 100px;">
        <label class="premium-label">
          <SvgIcon name="user" size="xs" /> Người tạo
        </label>
        <input v-model="filters.creator" placeholder="Nhập tên..." class="filter-control premium-input">
      </div>

      <div class="filter-actions flex items-end">
        <button class="btn-action btn-secondary flex items-center gap-2" @click="resetFilters" title="Đặt lại bộ lọc">
          <SvgIcon name="x" size="sm" /> <span>Đặt lại</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
      <span class="ms-2">Đang tải dữ liệu...</span>
    </div>
    <div v-else class="data-table-vxe">
      <vxe-table border round :data="filteredProfiles" :row-config="{ isHover: true }"
        :column-config="{ resizable: true }" :sort-config="{ trigger: 'cell' }">

        <vxe-column field="id" title="ID" width="80" sortable></vxe-column>

        <vxe-column field="name" title="Tên Hồ sơ" min-width="200" sortable></vxe-column>

        <vxe-column field="created_by_user_name" title="Người tạo" width="180" sortable>
          <template #default="{ row }">
            {{ row.created_by_user_name || 'Admin' }}
          </template>
        </vxe-column>

        <vxe-column field="created_at" title="Ngày tạo" width="150" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </vxe-column>

        <vxe-column field="form_view_name" title="Loại Form" width="180" sortable>
          <template #default="{ row }">
            <span class="badge-form" v-if="row.form_view_name">{{ row.form_view_name }}</span>
            <span v-else class="text-muted">Mặc định</span>
          </template>
        </vxe-column>

        <vxe-column field="status" title="Trạng thái" width="150" sortable>
          <template #default="{ row }">
            <div class="status-badge-container">
              <span class="status-badge" :class="row.status.toLowerCase()">
                {{ $t(row.status) }}
              </span>
            </div>
          </template>
        </vxe-column>

        <vxe-column title="Hành động" width="280" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <button v-if="auth.hasPermission('document_automation.change_loanprofile')" class="btn-action btn-edit"
                @click="editProfile(row.id)">Sửa</button>
              <button v-if="auth.hasPermission('document_automation.add_loanprofile')" class="btn-action btn-copy"
                @click="openDuplicateModal(row)">Sao chép</button>
              <button class="btn-action btn-doc" @click="openDownloadModal(row)">Xuất HĐ</button>
              <button v-if="auth.hasPermission('document_automation.delete_loanprofile')" class="btn-action btn-delete"
                @click="deleteProfile(row.id)">Xóa</button>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <!-- Contract Downloader Modal -->
    <ContractDownloader :isOpen="isModalOpen" :profileId="currentProfileId" :profileName="currentProfileName"
      @close="isModalOpen = false" />

    <!-- Confirm Delete Modal -->
    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa hồ sơ '${deleteTargetName}'? Hành động này không thể hoàn tác.`" confirmText="Xóa"
      @confirm="confirmDelete" @cancel="showDeleteModal = false" />

    <!-- Duplicate Modal -->
    <InputModal :visible="showDuplicateModal" title="Tạo bản sao hồ sơ" label="Tên hồ sơ mới:"
      :defaultValue="duplicateDefaultName" confirmText="Tạo bản sao" @confirm="confirmDuplicate"
      @cancel="showDuplicateModal = false" />

    <!-- Form Selection Modal (Refactored to BaseModal) -->
    <BaseModal :isOpen="showFormSelectModal" title="Chọn loại hồ sơ muốn tạo" :initialWidth="500"
      @close="showFormSelectModal = false">
      <div class="form-options">
        <button v-for="form in allForms" :key="form.id" class="form-option-item" @click="createNewProfile(form.slug)">
          <div class="option-icon">
            <SvgIcon name="file" size="lg" />
          </div>
          <div class="option-info">
            <div class="option-name">{{ form.name }}</div>
            <div class="option-note">{{ form.note || 'Mẫu hồ sơ tiêu chuẩn' }}</div>
          </div>
        </button>
      </div>
      <template #footer>
        <button class="btn-action btn-secondary" @click="showFormSelectModal = false">Đóng</button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import auth from '@/store/auth';
import ContractDownloader from '../components/ContractDownloader.vue';
import ConfirmModal from '../components/ConfirmModal.vue';
import InputModal from '../components/InputModal.vue';
import BaseModal from '../components/BaseModal.vue';
import SvgIcon from '../components/common/SvgIcon.vue';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';
import { errorHandlingMixin } from '@/utils/errorHandler';

export default {
  name: 'DashboardView',
  components: { ContractDownloader, ConfirmModal, InputModal, BaseModal, SvgIcon },
  mixins: [FilterableTableMixin, errorHandlingMixin],
  data() {
    return {
      auth,
      profiles: [],
      loading: true,
      filters: {
        search: '',
        status: null,
        createdDate: '',
        creator: ''
      },

      // State cho Modal
      isModalOpen: false,
      currentProfileId: null,
      currentProfileName: '',
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: '',
      // Duplicate Modal
      showDuplicateModal: false,
      duplicateTargetId: null,
      duplicateDefaultName: '',
      // Form Selection Modal
      showFormSelectModal: false,
      allForms: []
    }
  },
  mounted() {
    this.fetchProfiles();
    this.fetchForms();
  },
  computed: {
    filteredProfiles() {
      return this.filterArray(this.profiles, this.filters, {
        search: { type: 'text', fields: ['name', 'created_by_user_name', 'search_identifiers'] },
        status: { type: 'exact' },
        createdDate: { type: 'date', field: 'created_at' },
        creator: { type: 'text', field: 'created_by_user_name' }
      });
    }
  },
  methods: {
    async fetchProfiles(search = '') {
      try {
        const params = {};
        if (search) params.search = search;
        const response = await axios.get(`${API_URL}/loan-profiles/`, { params });
        this.profiles = response.data;
      } catch (error) {
        console.error(error);
        this.showError(error, 'Lỗi tải danh sách hồ sơ');
      } finally {
        this.loading = false;
      }
    },
    async fetchForms() {
      try {
        const response = await axios.get(`${API_URL}/form-views/`);
        this.allForms = response.data;
      } catch (error) {
        console.error("Lỗi load forms:", error);
      }
    },
    openFormSelectModal() {
      if (this.allForms.length === 0) {
        // Nếu không có form nào định nghĩa, đi tiếp tạo mặc định
        this.$router.push('/create');
      } else {
        this.showFormSelectModal = true;
      }
    },
    createNewProfile(slug) {
      this.showFormSelectModal = false;
      this.$router.push(`/create?form=${slug}`);
    },
    editProfile(id) {
      this.$router.push(`/edit/${id}`);
    },
    deleteProfile(id) {
      const profile = this.profiles.find(p => p.id === id);
      this.deleteTargetId = id;
      this.deleteTargetName = profile ? profile.name : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        try {
          await axios.delete(`${API_URL}/loan-profiles/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchProfiles();
        } catch (error) {
          this.showDeleteModal = false;
          this.showError(error, 'Lỗi khi xóa hồ sơ');
        }
      }
    },
    // THAY ĐỔI 6: Hàm mở Modal
    openDownloadModal(profile) {
      this.currentProfileId = profile.id;
      this.currentProfileName = profile.name;
      this.isModalOpen = true;
    },
    // Duplicate methods
    openDuplicateModal(profile) {
      this.duplicateTargetId = profile.id;
      this.duplicateDefaultName = `${profile.name} - copy`;
      this.showDuplicateModal = true;
    },
    async confirmDuplicate(newName) {
      try {
        const response = await axios.post(
          `${API_URL}/loan-profiles/${this.duplicateTargetId}/duplicate/`,
          { new_name: newName }
        );
        this.showDuplicateModal = false;
        this.duplicateTargetId = null;
        this.$toast.success(`Đã tạo bản sao: ${response.data.name}`);
        this.fetchProfiles();
      } catch (error) {
        this.showDuplicateModal = false;
        this.showError(error, 'Lỗi khi tạo bản sao');
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString('vi-VN');
    },
    resetFilters() {
      this.filters = {
        search: '',
        status: null,
        createdDate: '',
        creator: ''
      };
    }
  }
}
</script>

<style scoped>
.data-table-vxe {
  margin-top: 10px;
}

.form-options {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);
  max-height: 400px;
  overflow-y: auto;
  padding: var(--spacing-xs);
}

.form-option-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--slate-50);
  border: 2px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  text-align: left;
  transition: var(--transition-normal);
  width: 100%;
}

.form-option-item:hover {
  background: #e1f5fe;
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.option-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: var(--radius-md);
  color: var(--color-primary);
}

.option-name {
  font-weight: 700;
  font-size: var(--font-md);
  color: var(--slate-800);
}

.option-note {
  font-size: var(--font-sm);
  color: var(--slate-500);
  margin-top: 2px;
}

.premium-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--slate-600);
  margin-bottom: 6px;
  font-size: var(--font-xs);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.premium-input,
.premium-select {
  width: 80%;
  border: 1px solid var(--slate-200);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  background-color: white;
  transition: all 0.2s ease;
  font-size: var(--font-sm);
}

.premium-input:focus,
.premium-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-muted);
}
</style>

<template>
  <div class="dashboard-container page-container">
    <div class="header-actions">
      <h2>Danh sách Hồ sơ Vay</h2>
      <button v-if="auth.hasPermission('document_automation.add_loanprofile')" class="btn-action btn-create"
        @click="openFormSelectModal">+ Tạo Mới</button>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>Tìm kiếm</label>
        <input v-model="filters.search" placeholder="Tìm kiếm hồ sơ..." class="filter-control" style="width: 250px">
      </div>
      <div class="filter-group">
        <label>Trạng thái</label>
        <select v-model="filters.status" class="filter-control" style="width: 200px">
          <option :value="null">- Tất cả trạng thái -</option>
          <option value="DRAFT">Nháp</option>
          <option value="FINALIZED">Đã khóa</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Ngày tạo</label>
        <input v-model="filters.createdDate" type="date" class="filter-control" style="width: 150px">
      </div>
      <div class="filter-group">
        <label>Người tạo</label>
        <input v-model="filters.creator" placeholder="Nhập tên người tạo..." class="filter-control"
          style="width: 180px">
      </div>
      <button class="btn-action btn-secondary" @click="resetFilters">Đặt lại</button>
    </div>

    <div v-if="loading">Đang tải dữ liệu...</div>
    <div v-else class="ui-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="toggleSort('id')" :class="getSortableClass('id')">ID {{ getSortIcon('id') }}</th>
            <th @click="toggleSort('name')" :class="getSortableClass('name')">Tên Hồ sơ {{ getSortIcon('name') }}</th>
            <th @click="toggleSort('created_by_user_name', 'id')" :class="getSortableClass('created_by_user_name')">
              Người
              tạo {{ getSortIcon('created_by_user_name') }}</th>
            <th @click="toggleSort('created_at')" :class="getSortableClass('created_at')">Ngày tạo {{
              getSortIcon('created_at') }}</th>
            <th @click="toggleSort('form_view_name')" :class="getSortableClass('form_view_name')">Loại Form {{
              getSortIcon('form_view_name') }}</th>
            <th @click="toggleSort('status')" :class="getSortableClass('status')">Trạng thái {{ getSortIcon('status') }}
            </th>
            <th>Mã định danh (Số HĐ)</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="profile in sortedProfiles" :key="profile.id">
            <td>{{ profile.id }}</td>
            <td>{{ profile.name }}</td>
            <td>{{ profile.created_by_user_name || 'Admin' }}</td>
            <td>{{ formatDate(profile.created_at) }}</td>
            <td>
              <span class="badge-form" v-if="profile.form_view_name">{{ profile.form_view_name }}</span>
              <span v-else class="text-muted">Mặc định</span>
            </td>
            <td>
              <div class="status-badge-container">
                <span class="status-badge" :class="profile.status.toLowerCase()">
                  {{ $t(profile.status) }}
                </span>
              </div>
            </td>

            <td>
              <div v-if="profile.search_identifiers && profile.search_identifiers.length > 0">
                <span v-for="id in profile.search_identifiers" :key="id" class="badge-identifier">{{ id }}</span>
              </div>
            </td>
            <td>
              <button v-if="auth.hasPermission('document_automation.change_loanprofile')" class="btn-action btn-edit"
                @click="editProfile(profile.id)">Sửa</button>
              <button v-if="auth.hasPermission('document_automation.add_loanprofile')" class="btn-action btn-copy"
                @click="openDuplicateModal(profile)">Sao chép</button>
              <button class="btn-action btn-doc" @click="openDownloadModal(profile)">Xuất HĐ</button>
              <button v-if="auth.hasPermission('document_automation.delete_loanprofile')" class="btn-action btn-delete"
                @click="deleteProfile(profile.id)">Xóa</button>
            </td>
          </tr>
        </tbody>
      </table>
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

    <!-- Form Selection Modal -->
    <div v-if="showFormSelectModal" class="modal-overlay" @click.self="showFormSelectModal = false">
      <div class="modal-content form-select-modal">
        <h3>Chọn loại hồ sơ muốn tạo</h3>
        <div class="form-options">
          <button v-for="form in allForms" :key="form.id" class="form-option-item" @click="createNewProfile(form.slug)">
            <div class="option-icon">📄</div>
            <div class="option-info">
              <div class="option-name">{{ form.name }}</div>
              <div class="option-note">{{ form.note || 'Mẫu hồ sơ tiêu chuẩn' }}</div>
            </div>
          </button>
        </div>
        <div class="modal-footer">
          <button class="btn-action btn-secondary" @click="showFormSelectModal = false">Đóng</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import auth from '@/store/auth';
import ContractDownloader from '../components/ContractDownloader.vue';
import ConfirmModal from '../components/ConfirmModal.vue';
import InputModal from '../components/InputModal.vue';
import { makeTableResizable } from '@/utils/resizable-table';
import { SortableTableMixin } from '@/mixins/SortableTableMixin';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'DashboardView',
  components: { ContractDownloader, ConfirmModal, InputModal },
  mixins: [SortableTableMixin, FilterableTableMixin],
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
  watch: {
    'filters.search': {
      handler(newVal) {
        // Debounce search
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => {
          this.fetchProfiles(newVal);
        }, 500);
      }
    }
  },
  computed: {
    sortedProfiles() {
      const filtered = this.filterArray(this.profiles, this.filters, {
        search: { type: 'text', fields: ['name', 'created_by_user_name', 'search_identifiers'] },
        status: { type: 'exact' },
        createdDate: { type: 'date', field: 'created_at' },
        creator: { type: 'text', field: 'created_by_user_name' }
      });
      return this.sortArray(filtered);
    }
  },
  methods: {
    async fetchProfiles(search = '') {
      try {
        const params = {};
        if (search) params.search = search;
        const response = await axios.get('http://127.0.0.1:8000/api/loan-profiles/', { params });
        this.profiles = response.data;
      } catch (error) {
        console.error(error);
        this.$toast.error('Lỗi tải danh sách hồ sơ');
      } finally {
        this.loading = false;
        this.$nextTick(() => {
          this.initResizable();
        });
      }
    },
    initResizable() {
      const table = this.$el.querySelector('.data-table');
      if (table) {
        makeTableResizable(table, 'dashboard-profiles');
      }
    },
    async fetchForms() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/form-views/');
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
          await axios.delete(`http://127.0.0.1:8000/api/loan-profiles/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchProfiles();
        } catch (error) {
          console.error(error);
          this.$toast.error('Lỗi khi xóa hồ sơ!');
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
          `http://127.0.0.1:8000/api/loan-profiles/${this.duplicateTargetId}/duplicate/`,
          { new_name: newName }
        );
        this.showDuplicateModal = false;
        this.duplicateTargetId = null;
        this.$toast.success(`Đã tạo bản sao: ${response.data.name}`);
        this.fetchProfiles();
      } catch (error) {
        console.error(error);
        this.$toast.error('Lỗi khi tạo bản sao!');
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
/* Scoped overrides if any */
.form-select-modal {
  width: 500px;
  max-width: 90%;
}

.form-options {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 5px;
}

.form-option-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  width: 100%;
}

.form-option-item:hover {
  background: #e1f5fe;
  border-color: #0288d1;
  transform: translateY(-2px);
}

.option-icon {
  font-size: 24px;
}

.option-name {
  font-weight: bold;
  font-size: 1.1em;
  color: #2c3e50;
}

.option-note {
  font-size: 0.9em;
  color: #7f8c8d;
  margin-top: 4px;
}

.badge-identifier {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85em;
  margin-right: 4px;
  border: 1px solid #bbdefb;
}
</style>

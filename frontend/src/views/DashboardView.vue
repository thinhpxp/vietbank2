<template>
  <div class="dashboard-container page-container">
    <div class="header-actions">
      <h2>Danh sách Hồ sơ Vay</h2>
      <button v-if="auth.hasPermission('document_automation.add_loanprofile')" class="btn-action btn-create"
        @click="openFormSelectModal">+ Tạo Mới</button>
    </div>

    <div v-if="loading">Đang tải dữ liệu...</div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Tên Hồ sơ</th>
          <th>Người tạo</th>
          <th>Ngày tạo</th>
          <th>Loại Form</th>
          <th>Trạng thái</th>
          <th>Hành động</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="profile in profiles" :key="profile.id">
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
              <span v-if="profile.status === 'FINALIZED'" class="status-badge finalized">🔒 ĐÃ KHÓA</span>
              <span v-else class="status-badge draft">✍️ NHÁP</span>
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

export default {
  name: 'DashboardView',
  components: { ContractDownloader, ConfirmModal, InputModal },
  data() {
    return {
      auth,
      profiles: [],
      loading: true,

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
  methods: {
    async fetchProfiles() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/loan-profiles/');
        this.profiles = response.data;
      } catch (error) {
        console.error(error);
        this.$toast.error('Lỗi tải danh sách hồ sơ');
      } finally {
        this.loading = false;
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
.option-icon { font-size: 24px; }
.option-name { font-weight: bold; font-size: 1.1em; color: #2c3e50; }
.option-note { font-size: 0.9em; color: #7f8c8d; margin-top: 4px; }
</style>

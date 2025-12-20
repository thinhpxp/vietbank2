<template>
  <div class="dashboard-container">
    <div class="header-actions">
      <h2>Danh sách Hồ sơ Vay</h2>
      <button class="btn-create" @click="$router.push('/create')">+ Tạo Mới</button>
    </div>

    <div v-if="loading">Đang tải dữ liệu...</div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Tên Hồ sơ</th>
          <th>Người tạo</th>
          <th>Ngày tạo</th>
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
            <button class="btn-edit" @click="editProfile(profile.id)">Sửa</button>

            <!-- THAY ĐỔI 1: Gọi hàm mở Modal thay vì alert -->
            <button class="btn-doc" @click="openDownloadModal(profile)">Xuất HĐ</button>
            <button class="btn-delete" @click="deleteProfile(profile.id)">Xóa</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- THAY ĐỔI 2: Nhúng Component Modal vào đây -->
    <ContractDownloader
      :isOpen="isModalOpen"
      :profileId="currentProfileId"
      :profileName="currentProfileName"
      @close="isModalOpen = false"
    />
  </div>
</template>

<script>
import axios from 'axios';
// THAY ĐỔI 3: Import Component
import ContractDownloader from '../components/ContractDownloader.vue';

export default {
  name: 'DashboardView',
  // THAY ĐỔI 4: Khai báo Component
  components: { ContractDownloader },
  data() {
    return {
      profiles: [],
      loading: true,

      // THAY ĐỔI 5: State cho Modal
      isModalOpen: false,
      currentProfileId: null,
      currentProfileName: ''
    }
  },
  mounted() {
    this.fetchProfiles();
  },
  methods: {
    async fetchProfiles() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/loan-profiles/');
        this.profiles = response.data;
      } catch (error) {
        console.error(error);
        alert('Lỗi tải danh sách hồ sơ');
      } finally {
        this.loading = false;
      }
    },
    editProfile(id) {
      this.$router.push(`/edit/${id}`);
    },
    async deleteProfile(id) {
      if (confirm('Bạn có chắc chắn muốn xóa hồ sơ này không? Hành động này không thể hoàn tác.')) {
        try {
          await axios.delete(`http://127.0.0.1:8000/api/loan-profiles/${id}/`);
          alert('Đã xóa hồ sơ thành công!');
          this.fetchProfiles(); // Refresh list
        } catch (error) {
          console.error(error);
          alert('Lỗi khi xóa hồ sơ!');
        }
      }
    },
    // THAY ĐỔI 6: Hàm mở Modal
    openDownloadModal(profile) {
      this.currentProfileId = profile.id;
      this.currentProfileName = profile.name;
      this.isModalOpen = true;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString('vi-VN');
    }
  }
}
</script>

<style scoped>
.dashboard-container { max-width: 1000px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-create { background: #42b983; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 16px; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
.data-table th { background: #f8f9fa; color: #333; }
.btn-edit { background: #3498db; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px; }
.btn-doc { background: #e67e22; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px; }
.btn-delete { background: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
</style>
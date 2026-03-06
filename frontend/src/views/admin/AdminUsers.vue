<template>
  <div class="admin-page">
    <h2>Quản lý Người dùng</h2>

    <!-- Form tạo User mới -->
    <div class="admin-panel mb-6">
      <h4>Tạo tài khoản mới</h4>
      <div class="admin-row mb-2">
        <input v-model="newUser.username" placeholder="Tên đăng nhập (*)" class="admin-input">
        <input v-model="newUser.email" placeholder="Email" type="email" class="admin-input">
        <input v-model="newUser.password" placeholder="Mật khẩu (*)" type="password" class="admin-input">
      </div>
      <div class="admin-row items-center">
        <input v-model="newUser.note" placeholder="Ghi chú (Chức vụ, Phòng ban...)" style="flex: 2" class="admin-input">
        <label class="admin-checkbox-label">
          <input type="checkbox" v-model="newUser.is_staff"> Là Admin/Staff?
        </label>
        <button @click="addUser" class="btn-action btn-success">🚀 Tạo User</button>
      </div>
    </div>

    <div class="filter-bar mb-4">
      <div class="filter-group">
        <label>Tìm kiếm:</label>
        <input v-model="filters.search" placeholder="Tìm theo username hoặc email..." class="admin-form-control"
          style="width: 300px">
      </div>
    </div>

    <!-- Danh sách User -->
    <div class="data-table-vxe">
      <vxe-table border round :data="filteredUsers" :row-config="{ isHover: true }" :column-config="{ resizable: true }"
        :sort-config="{ trigger: 'cell', defaultSort: { field: 'id', order: 'desc' } }">
        <vxe-column field="id" title="ID" width="60" sortable></vxe-column>
        <vxe-column field="username" title="Username" min-width="150" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.username" class="vxe-input-minimal">
            <strong v-else>{{ row.username }}</strong>
          </template>
        </vxe-column>
        <vxe-column field="email" title="Email" min-width="200" sortable>
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.email" class="vxe-input-minimal">
            <span v-else>{{ row.email }}</span>
          </template>
        </vxe-column>
        <vxe-column field="note" title="Ghi chú" min-width="150">
          <template #default="{ row }">
            <input v-if="editingId === row.id" v-model="row.note" class="vxe-input-minimal">
            <span v-else>{{ row.note }}</span>
          </template>
        </vxe-column>
        <vxe-column field="is_staff" title="Vai trò" width="120">
          <template #default="{ row }">
            <select v-if="editingId === row.id" v-model="row.is_staff" class="vxe-input-minimal">
              <option :value="true">Admin</option>
              <option :value="false">User</option>
            </select>
            <template v-else>
              <span v-if="row.is_staff" class="badge-admin">Admin</span>
              <span v-else class="badge badge-inactive">User</span>
            </template>
          </template>
        </vxe-column>
        <vxe-column field="is_active" title="Trạng thái" width="120">
          <template #default="{ row }">
            <select v-if="editingId === row.id" v-model="row.is_active" class="vxe-input-minimal">
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
            <template v-else>
              <span :class="['status-badge', row.is_active ? 'finalized' : 'draft']">
                {{ row.is_active ? 'Active' : 'Inactive' }}
              </span>
            </template>
          </template>
        </vxe-column>
        <vxe-column title="Hành động" width="160" fixed="right">
          <template #default="{ row }">
            <div class="flex gap-2">
              <template v-if="editingId === row.id">
                <button @click="updateUser(row)" class="btn-action btn-save btn-icon-only" title="Lưu">
                  <SvgIcon name="save" size="sm" />
                </button>
                <button @click="editingId = null" class="btn-action btn-secondary btn-icon-only" title="Hủy">
                  <SvgIcon name="x" size="sm" />
                </button>
              </template>
              <template v-else>
                <button @click="editingId = row.id" class="btn-action btn-edit btn-icon-only" title="Sửa">
                  <SvgIcon name="edit" size="sm" />
                </button>
                <button @click="deleteUser(row.id)" class="btn-action btn-delete btn-icon-only" title="Xóa">
                  <SvgIcon name="trash" size="sm" />
                </button>
              </template>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa người dùng '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />

    <!-- Hệ thống Modal Toàn cục (kế thừa từ mixin) -->
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
  name: 'AdminUsers',
  components: { ConfirmModal },
  mixins: [errorHandlingMixin, FilterableTableMixin],
  data() {
    return {
      users: [],
      editingId: null,
      newUser: {
        username: '',
        password: '',
        email: '',
        is_staff: false,
        note: ''
      },
      showDeleteModal: false,
      deleteTargetId: null,
      deleteTargetName: '',
      filters: { search: '' }
    }
  },
  computed: {
    filteredUsers() {
      return this.filterArray(this.users, this.filters, {
        search: { type: 'text', fields: ['username', 'email'] }
      });
    }
  },
  watch: {
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await axios.get(`${API_URL}/users/`);
        this.users = response.data;
      } catch (error) {
        console.error("Lỗi tải users:", error);
      }
    },
    async updateUser(user) {
      try {
        const payload = { ...user };
        delete payload.password;

        await axios.patch(`${API_URL}/users/${user.id}/`, payload);
        this.editingId = null;
        this.$toast.success(`Cập nhật thông tin người dùng '${user.username}' thành công!`);
        await this.fetchUsers();
      } catch (error) {
        console.error(error);
        this.showError(error, 'Lỗi khi cập nhật user');
      }
    },
    async addUser() {
      if (!this.newUser.username || !this.newUser.password) {
        this.showWarning('Vui lòng nhập Username và Password!', 'Thiếu thông tin');
        return;
      }

      try {
        await axios.post(`${API_URL}/users/`, this.newUser);
        this.$toast.success(`Tạo người dùng '${this.newUser.username}' thành công!`);

        // Reset form
        this.newUser = { username: '', password: '', email: '', is_staff: false };
        this.fetchUsers();
      } catch (error) {
        console.error(error);
        this.showError(error, 'Lỗi khi tạo user');
      }
    },
    deleteUser(id) {
      const user = this.users.find(u => u.id === id);
      this.deleteTargetId = id;
      this.deleteTargetName = user ? user.username : '';
      this.showDeleteModal = true;
    },
    async confirmDelete() {
      if (this.deleteTargetId) {
        try {
          await axios.delete(`${API_URL}/users/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.$toast.success(`Đã xóa người dùng '${this.deleteTargetName}' khỏi hệ thống.`);
          this.deleteTargetId = null;
          this.fetchUsers();
        } catch (error) {
          this.showError(error, 'Lỗi khi xóa user');
        }
      }
    }
  }
}
</script>

<style scoped>
/* Scoped styles removed as they are now standardized in common-ui.css */
</style>
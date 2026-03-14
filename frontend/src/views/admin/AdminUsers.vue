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
        <button @click="addUser" class="btn-action btn-create">🚀 Tạo User</button>
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
        <vxe-column title="Hành động" width="220" fixed="right">
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
                <button @click="editUserExt(row)" class="btn-action btn-primary btn-icon-only" title="Thông tin mở rộng">
                  <SvgIcon name="user-plus" size="sm" />
                </button>
                <button @click="editingId = row.id" class="btn-action btn-edit btn-icon-only" title="Sửa cơ bản">
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

    <!-- Modal sửa thông tin mở rộng -->
    <BaseModal v-if="showExtModal" :visible="showExtModal" title="Thông tin người dùng mở rộng" @close="showExtModal = false">
      <div v-if="loadingExt" class="p-4 text-center">Đang tải cấu hình...</div>
      <div v-else class="p-4">
        <p class="mb-4 text-sm text-gray-500">Đang hiệu chỉnh: <strong>{{ selectedUser?.username }}</strong></p>
        <DynamicForm 
          v-if="dynamicGroups"
          :groups="dynamicGroups" 
          :initial-values="selectedUser?.field_values || {}"
          mode="horizontal"
          @update:values="val => selectedUserExtValues = val"
        />
      </div>
      <template #footer>
        <button class="btn-action btn-secondary" @click="showExtModal = false">Hủy</button>
        <button class="btn-action btn-save" @click="saveUserExt" :disabled="savingExt">
          {{ savingExt ? 'Đang lưu...' : 'Lưu thông tin mở rộng' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import SystemService from '@/services/system.service';
import MasterService from '@/services/master.service';
import UserService from '@/services/user.service';
import SvgIcon from '@/components/common/SvgIcon.vue';
import ConfirmModal from '../../components/ConfirmModal.vue';
import BaseModal from '../../components/BaseModal.vue';
import DynamicForm from '@/components/DynamicForm.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'AdminUsers',
  title: 'Quản lý Người dùng',
  components: { ConfirmModal, BaseModal, DynamicForm, SvgIcon },
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
      filters: { search: '' },

      // USER_EXT data
      showExtModal: false,
      loadingExt: false,
      savingExt: false,
      selectedUser: null,
      selectedUserExtValues: {},
      dynamicGroups: {}
    }
  },
  computed: {
    filteredUsers() {
      return this.filterArray(this.users, this.filters, {
        search: { type: 'text', fields: ['username', 'email'] }
      });
    }
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await SystemService.getUsers();
        this.users = response.data;
      } catch (error) {
        this.showError(error, 'Lỗi tải danh sách người dùng');
      }
    },
    async updateUser(user) {
      try {
        const payload = { ...user };
        delete payload.password;

        await SystemService.updateUser(user.id, payload);
        this.editingId = null;
        this.$toast.success(`Cập nhật thông tin người dùng '${user.username}' thành công!`);
        await this.fetchUsers();
      } catch (error) {
        this.showError(error, 'Lỗi khi cập nhật user');
      }
    },
    async addUser() {
      if (!this.newUser.username || !this.newUser.password) {
        this.showWarning('Vui lòng nhập Username và Password!', 'Thiếu thông tin');
        return;
      }

      try {
        await SystemService.createUser(this.newUser);
        this.$toast.success(`Tạo người dùng '${this.newUser.username}' thành công!`);

        // Reset form
        this.newUser = { username: '', password: '', email: '', is_staff: false, note: '' };
        this.fetchUsers();
      } catch (error) {
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
          await SystemService.deleteUser(this.deleteTargetId);
          this.showDeleteModal = false;
          this.$toast.success(`Đã xóa người dùng '${this.deleteTargetName}' khỏi hệ thống.`);
          this.deleteTargetId = null;
          this.fetchUsers();
        } catch (error) {
          this.showDeleteModal = false;
          this.showError(error, 'Lỗi khi xóa user');
        }
      }
    },
    async editUserExt(user) {
      this.selectedUser = user;
      this.selectedUserExtValues = user.field_values || {};
      this.showExtModal = true;
      this.loadingExt = true;
      try {
        const res = await MasterService.getActiveFieldsGrouped('USER_EXT');
        this.dynamicGroups = res.data;
      } catch (e) {
        this.$toast.error('Lỗi khi tải cấu hình trường động');
      } finally {
        this.loadingExt = false;
      }
    },
    async saveUserExt() {
      this.savingExt = true;
      try {
        await SystemService.updateUser(this.selectedUser.id, {
          field_values: this.selectedUserExtValues
        });
        this.$toast.success('Cập nhật thông tin mở rộng thành công');
        this.showExtModal = false;
        this.fetchUsers();
      } catch (e) {
        this.showError(e, 'Lỗi khi lưu thông tin mở rộng');
      } finally {
        this.savingExt = false;
      }
    }
  }
}
</script>

<style scoped>
/* Scoped styles removed as they are now standardized in common-ui.css */
</style>
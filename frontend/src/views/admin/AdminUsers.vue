<template>
  <div class="admin-page">
    <h2>Quản lý Người dùng</h2>

    <!-- Form tạo User mới -->
    <div class="add-box">
      <h4>Tạo tài khoản mới</h4>
      <div class="row">
        <input v-model="newUser.username" placeholder="Tên đăng nhập (*)">
        <input v-model="newUser.email" placeholder="Email" type="email">
      </div>
      <div class="row">
        <input v-model="newUser.note" placeholder="Ghi chú (Chức vụ, Phòng ban...)" style="flex: 2">
        <input v-model="newUser.password" placeholder="Mật khẩu (*)" type="password">
        <label class="checkbox-label">
          <input type="checkbox" v-model="newUser.is_staff"> Là Admin/Staff?
        </label>
        <button @click="addUser" class="btn-action btn-create">Tạo User</button>
      </div>
    </div>

    <!-- Danh sách User -->
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Email</th>
          <th>Ghi chú</th>
          <th>Vai trò</th>
          <th>Trạng thái</th>
          <th>Hành động</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.id }}</td>
          <td>
            <input v-if="editingId === u.id" v-model="u.username" class="inline-edit">
            <strong v-else>{{ u.username }}</strong>
          </td>
          <td>
            <input v-if="editingId === u.id" v-model="u.email" class="inline-edit">
            <span v-else>{{ u.email }}</span>
          </td>
          <td>
            <input v-if="editingId === u.id" v-model="u.note" class="inline-edit">
            <span v-else>{{ u.note }}</span>
          </td>
          <td>
            <select v-if="editingId === u.id" v-model="u.is_staff" class="inline-edit">
              <option :value="true">Admin</option>
              <option :value="false">User</option>
            </select>
            <template v-else>
              <span v-if="u.is_staff" class="badge admin">Admin</span>
              <span v-else class="badge user">User</span>
            </template>
          </td>
          <td>
            <select v-if="editingId === u.id" v-model="u.is_active" class="inline-edit">
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
            <template v-else>
              <span v-if="u.is_active" class="status active">Active</span>
              <span v-else class="status inactive">Inactive</span>
            </template>
          </td>
          <td>
            <div class="action-group">
              <button v-if="editingId === u.id" @click="updateUser(u)" class="btn-action btn-save">Lưu</button>
              <button v-else @click="editingId = u.id" class="btn-action btn-edit">Sửa</button>
              <button @click="deleteUser(u.id)" class="btn-action btn-delete">Xóa</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
      :message="`Bạn có chắc muốn xóa người dùng '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
      @cancel="showDeleteModal = false" />
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { makeTableResizable } from '../../utils/resizable-table';

export default {
  name: 'AdminUsers',
  components: { ConfirmModal },
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
      deleteTargetName: ''
    }
  },
  mounted() {
    this.fetchUsers();
    this.initResizable();
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/users/');
        this.users = response.data;
      } catch (error) {
        console.error("Lỗi tải users:", error);
      } finally {
        this.$nextTick(() => this.initResizable());
      }
    },
    initResizable() {
      const table = this.$el.querySelector('.data-table');
      if (table) {
        makeTableResizable(table, 'admin-users');
      }
    },
    async updateUser(user) {
      try {
        // Không gửi mật khẩu khi cập nhật thông tin. Việc đổi mật khẩu nên có một form riêng.
        const payload = { ...user };
        delete payload.password;

        await axios.patch(`http://127.0.0.1:8000/api/users/${user.id}/`, payload);
        this.editingId = null;
        await this.fetchUsers(); // Tải lại để đảm bảo dữ liệu đồng bộ
      } catch (error) {
        console.error(error);
        alert("Lỗi khi cập nhật user: " + JSON.stringify(error.response?.data));
      }
    },
    async addUser() {
      if (!this.newUser.username || !this.newUser.password) {
        return alert("Vui lòng nhập Username và Password!");
      }

      try {
        await axios.post('http://127.0.0.1:8000/api/users/', this.newUser);
        alert("Tạo người dùng thành công!");

        // Reset form
        this.newUser = { username: '', password: '', email: '', is_staff: false };
        this.fetchUsers();
      } catch (error) {
        console.error(error);
        alert("Lỗi khi tạo user: " + JSON.stringify(error.response?.data));
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
          await axios.delete(`http://127.0.0.1:8000/api/users/${this.deleteTargetId}/`);
          this.showDeleteModal = false;
          this.deleteTargetId = null;
          this.fetchUsers();
        } catch (error) {
          alert("Lỗi khi xóa user");
        }
      }
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

.row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.row input {
  padding: 8px;
  flex: 1;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: bold;
  cursor: pointer;
}

.action-group {
  display: flex;
  gap: 5px;
}

.inline-edit {
  padding: 5px;
  width: 100%;
  box-sizing: border-box;
}

.badge.admin {
  background-color: #8e44ad;
  color: white;
}

.badge.user {
  background-color: #3498db;
  color: white;
}

.status {
  font-weight: bold;
  font-size: 0.8rem;
}

.status.active {
  color: #27ae60;
}

.status.inactive {
  color: #7f8c8d;
}
</style>
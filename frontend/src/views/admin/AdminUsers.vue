<template>
  <div>
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
        <button @click="addUser" class="btn-create">Tạo User</button>
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
            <button v-if="editingId === u.id" @click="updateUser(u)" class="btn-save">Lưu</button>
            <button v-else @click="editingId = u.id" class="btn-edit">Sửa</button>
            <button @click="deleteUser(u.id)" class="btn-delete">Xóa</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminUsers',
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
      }
    }
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/users/');
        this.users = response.data;
      } catch (error) {
        console.error("Lỗi tải users:", error);
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
    async deleteUser(id) {
      if (confirm("Bạn có chắc chắn muốn xóa người dùng này?")) {
        try {
          await axios.delete(`http://127.0.0.1:8000/api/users/${id}/`);
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
.add-box { background: #eee; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
.row { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
.row input { padding: 8px; flex: 1; border: 1px solid #ccc; border-radius: 4px; }
.checkbox-label { display: flex; align-items: center; gap: 5px; font-weight: bold; cursor: pointer; }
.btn-create { background: #42b983; color: white; border: none; padding: 8px 15px; cursor: pointer; border-radius: 4px; }
.btn-edit { background: #3498db; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px; }
.btn-save { background: #2ecc71; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px; }
.data-table { width: 100%; border-collapse: collapse; background: white; }
.data-table th, .data-table td { padding: 10px; border: 1px solid #ddd; text-align: left; }
.btn-delete { background: #e74c3c; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px; margin-left: 5px; }
.inline-edit { padding: 5px; width: 100%; box-sizing: border-box; }

/* Badges */
.badge { padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; color: white; }
.badge.admin { background-color: #8e44ad; }
.badge.user { background-color: #3498db; }

.status { font-weight: bold; font-size: 0.8rem; }
.status.active { color: #27ae60; }
.status.inactive { color: #7f8c8d; }
</style>
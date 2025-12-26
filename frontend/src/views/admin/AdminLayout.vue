<template>
  <div class="admin-container">
    <aside class="sidebar">
      <h3>Admin Panel</h3>
      <nav>
        <router-link to="/admin/groups">📂 Quản lý Nhóm Thông tin</router-link>
        <router-link to="/admin/fields">📝 Quản lý Trường Thông tin</router-link>
        <router-link to="/admin/templates">📄 Mẫu Hợp đồng</router-link>
        <router-link to="/admin/roles">🎭 Quản lý Vai trò</router-link>
        <router-link to="/admin/forms">📑 Cấu hình Form</router-link>
        <router-link to="/admin/users">👤 Người dùng</router-link>
        <hr>
        <router-link to="/">🏠 Về Dashboard</router-link>
      </nav>
    </aside>
    <main class="content">
      <router-view /> <!-- Nội dung con sẽ hiện ở đây -->
    </main>
  </div>
</template>
<style scoped>
.admin-container {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 250px;
  background: #34495e;
  color: white;
  padding: 20px;
}

.sidebar a {
  display: block;
  color: #ecf0f1;
  padding: 10px;
  text-decoration: none;
  margin-bottom: 5px;
  border-radius: 4px;
}

.sidebar a.router-link-active {
  background: #42b983;
}

.content {
  flex: 1;
  padding: 20px;
  background: #f4f6f8;
}
</style>
<template>
  <div class="admin-container" :class="{ 'sidebar-collapsed': isCollapsed }">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h3>Admin Panel</h3>
      </div>
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
      <button class="toggle-btn" @click="isCollapsed = !isCollapsed" :title="isCollapsed ? 'Hiện menu' : 'Ẩn menu'">
        {{ isCollapsed ? '▶' : '◀' }}
      </button>
      <router-view /> <!-- Nội dung con sẽ hiện ở đây -->
    </main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isCollapsed: false
    };
  }
};
</script>

<style scoped>
.admin-container {
  display: flex;
  min-height: 100vh;
  position: relative;
}

.sidebar {
  width: 250px;
  background: #34495e;
  color: white;
  padding: 20px;
  transition: all 0.3s ease;
  overflow-x: hidden;
  white-space: nowrap;
}

.sidebar-collapsed .sidebar {
  width: 0;
  padding: 20px 0;
  opacity: 0;
  pointer-events: none;
}

.sidebar-header {
  margin-bottom: 20px;
}

.sidebar h3 {
  margin: 0;
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
  transition: all 0.3s ease;
  position: relative;
}

.toggle-btn {
  position: absolute;
  left: 0;
  top: 15px;
  transform: translateX(-50%);
  background: #2c3e50;
  color: white;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.sidebar-collapsed .toggle-btn {
  left: 10px;
  transform: translateX(0);
}

.toggle-btn:hover {
  background: #42b983;
}

@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    height: 100%;
    z-index: 99;
  }
}
</style>
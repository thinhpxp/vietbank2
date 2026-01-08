<template>
  <div class="admin-layout" :class="{ 'is-collapsed': isCollapsed }">
    <!-- Sidebar -->
    <aside class="layout-sidebar">
      <header class="sidebar-header">
        <h3>Admin Panel</h3>
      </header>

      <nav class="sidebar-nav">
        <router-link to="/admin/groups">📂 Quản lý Nhóm</router-link>
        <router-link to="/admin/fields">📝 Trường</router-link>
        <router-link to="/admin/templates">📄 Mẫu</router-link>
        <router-link to="/admin/roles">🎭 Vai trò</router-link>
        <router-link to="/admin/forms">📑 Form</router-link>
        <router-link to="/admin/users">👤 Người dùng</router-link>
        <router-link to="/admin/object-types">🏷️ Loại Đối tượng</router-link>
        <router-link to="/admin/master-data">🗂️ Dữ liệu gốc</router-link>
        <hr />
        <router-link to="/">🏠 Dashboard</router-link>
      </nav>
    </aside>

    <!-- Main -->
    <main class="layout-main">
      <router-view />
    </main>

    <!-- Global Toggle -->
    <button class="layout-toggle" @click="isCollapsed = !isCollapsed" :aria-expanded="!isCollapsed"
      :title="isCollapsed ? 'Mở menu' : 'Đóng menu'">
      {{ isCollapsed ? '▶' : '◀' }}
    </button>
  </div>
</template>


<script>
export default {
  name: 'AdminLayout',
  data() {
    return {
      isCollapsed: false
    };
  }
};
</script>

<style>
@import "@/assets/admin.css";

/* =========================
   DESIGN TOKENS
========================= */
.admin-layout {
  --sidebar-width: 250px;
  --sidebar-bg: #34495e;
  --main-bg: #f4f6f8;
  --toggle-size: 30px;
}

/* =========================
   LAYOUT SHELL
========================= */
.admin-layout {
  display: flex;
  min-height: 100vh;
  position: relative;
}


/* =========================
   SIDEBAR
========================= */
.layout-sidebar {
  text-align: left;
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  color: white;
  /* padding: 20px; */
  transition: width 0.3s ease, opacity 0.3s ease;
  overflow: hidden;
}

.admin-layout.is-collapsed {
  --sidebar-width: 0px;
}

.admin-layout.is-collapsed .layout-sidebar {
  opacity: 0;
  pointer-events: none;
}

/* =========================
   NAV
========================= */
.sidebar-nav a {
  display: block;
  padding: 10px;
  color: #ecf0f1;
  text-decoration: none;
  border-radius: 4px;
}

.sidebar-nav a.router-link-active {
  background: #42b983;
}

/* =========================
   MAIN CONTENT
========================= */
.layout-main {
  flex: 1;
  padding: 20px;
  background: var(--main-bg);
  overflow-y: auto;
  text-align: left;
  /* Chèn ghi đè text-align: center từ App.vue */
}

/* =========================
   TOGGLE BUTTON
========================= */
.layout-toggle {
  position: fixed;
  top: 15px;
  left: var(--sidebar-width);
  transform: translateX(-50%);
  width: var(--toggle-size);
  height: var(--toggle-size);

  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;

  display: flex;
  align-items: center;
  justify-content: center;

  z-index: 1000;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: left 0.3s ease, transform 0.3s ease;
}

.admin-layout.is-collapsed .layout-toggle {
  left: 10px;
  transform: none;
}

/* =========================
   HOVER
========================= */
.layout-toggle:hover {
  background: #42b983;
}

/* =========================
   MOBILE
========================= */
@media (max-width: 768px) {
  .layout-sidebar {
    position: fixed;
    height: 100vh;
    z-index: 999;
  }
}
</style>
<template>
  <div id="app">
    <!-- Thanh điều hướng chung (Ẩn khi ở trang Login/Register) -->
    <nav v-if="!hideNavbar" class="navbar">
      <div class="brand">AutoContract App</div>
      <div class="links">
        <router-link to="/">Danh sách Hồ sơ</router-link>
        <router-link v-if="isAuthenticated" to="/master-data">
          <SvgIcon name="folder" size="sm" /> Dữ liệu gốc
        </router-link>
        <router-link v-if="isAdmin" to="/admin/groups">
          <SvgIcon name="settings" size="sm" /> Admin Panel
        </router-link>
      </div>

      <div v-if="isAuthenticated" class="user-info">
        <router-link to="/profile" class="user-profile-link">
          <span class="user-avatar">
            <SvgIcon name="user" size="md" />
          </span>
          <span class="user-name">{{ userDisplayName }}</span>
        </router-link>
        <button @click="logout" class="btn-action btn-logout">
          <SvgIcon name="logout" size="sm" /> Đăng xuất
        </button>
      </div>
    </nav>

    <!-- Nơi nội dung của từng trang sẽ hiển thị -->
    <router-view />
    <!-- Thông báo góc màn hình -->
    <AppToast />
  </div>
</template>

<script>
import AppToast from './components/AppToast.vue'
import auth from './store/auth'

export default {
  name: 'App',
  components: { AppToast },
  computed: {
    isAuthenticated() { return auth.state.isAuthenticated },
    isAdmin() { return auth.isAdmin.value },
    userDisplayName() {
      return auth.state.user?.profile?.full_name || auth.state.user?.username || 'User'
    },
    hideNavbar() {
      return ['Login', 'Register'].includes(this.$route.name)
    }
  },
  methods: {
    logout() {
      auth.logout();
      this.$router.push('/login');
    }
  }
}
</script>

<style>
/* CSS cơ bản cho đẹp */
body {
  margin: 0;
  background-color: #f4f6f8;
  font-family: sans-serif;
}

#app {
  text-align: center;
  color: #2c3e50;
}

.navbar {
  background: #0366d6;
  padding: 15px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  font-weight: bold;
  font-size: 1.2rem;
}

.links a {
  color: #ecf0f1;
  text-decoration: none;
  margin: 0 15px;
  font-weight: 500;
  font-size: larger;
}

.links a.router-link-active {
  color: #ffffff;
  font-weight: 700;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-profile-link {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 5px 15px;
  border-radius: 20px;
  text-decoration: none;
  color: white;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-profile-link:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  border-color: #42b983;
}

.user-name {
  font-size: 0.95rem;
  font-weight: 600;
}

.user-avatar {
  font-size: 1.1rem;
}

.btn-logout {
  background: var(--color-danger);
  color: white;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.btn-logout:hover {
  background: #c0392b;
}
</style>
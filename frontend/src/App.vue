<template>
  <div id="app">
    <!-- Thanh điều hướng chung (Ẩn khi ở trang Login/Register) -->
    <nav v-if="!hideNavbar" class="navbar">
      <div class="brand">Vietbank Contract App</div>
      <div class="links">
        <router-link to="/">Danh sách Hồ sơ</router-link>
        <router-link v-if="isAdmin" to="/admin" style="color: #f1c40f">Admin Panel</router-link>
      </div>

      <div v-if="isAuthenticated" class="user-info">
        <span class="user-name">👤 {{ userDisplayName }}</span>
        <button @click="logout" class="btn-logout">Đăng xuất</button>
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
  background: #2c3e50;
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
}

.links a.router-link-active {
  color: #42b983;
  font-weight: 700;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  font-size: 0.9rem;
  opacity: 0.9;
}

.btn-logout {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.btn-logout:hover {
  background: #c0392b;
}
</style>
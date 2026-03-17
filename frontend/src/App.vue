<template>
  <div id="app">
    <!-- Thanh điều hướng chung (Ẩn khi ở trang Login/Register) -->
    <nav v-if="!hideNavbar" class="navbar">
      <div class="brand">
        <template v-if="systemStore.logoType === 'image' && systemStore.logoUrl">
          <img :src="systemStore.logoUrl" alt="Logo" class="brand-logo-img" />
        </template>
        <template v-else>
          <div class="brand-icon-wrapper">
            <SvgIcon name="layers" size="md" />
          </div>
        </template>
        <span class="brand-text">{{ systemStore.brandName }}</span>
      </div>

      <div class="links">
        <router-link to="/">
          <SvgIcon name="clipboard" size="sm" /> Danh sách Hồ sơ
        </router-link>
        <router-link v-if="isAuthenticated" to="/master-data">
          <SvgIcon name="database" size="sm" /> Dữ liệu gốc
        </router-link>
        <router-link v-if="isAdmin" to="/admin/groups"
          :class="{ 'router-link-active': $route.path.startsWith('/admin') }">
          <SvgIcon name="settings" size="sm" /> Admin Panel
        </router-link>
      </div>

      <div v-if="isAuthenticated" class="user-info">
        <NotificationPanel />
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

    <!-- Global Error Modal -->
    <ConfirmModal :visible="showErrorModal" :title="errorModalTitle" :message="errorModalMessage"
      :errorCode="errorModalCode" :details="errorModalDetails" type="error" mode="alert" confirmText="Đóng"
      :showTimestamp="true" @confirm="closeErrorModal" @cancel="closeErrorModal" :closeOnOverlay="true" />

    <!-- Global Success Modal -->
    <ConfirmModal :visible="showSuccessModal" :title="successModalTitle" :message="successModalMessage" type="success"
      mode="alert" confirmText="OK" @confirm="showSuccessModal = false" @cancel="showSuccessModal = false" />

    <!-- Global Warning Modal -->
    <ConfirmModal :visible="showWarningModal" :title="warningModalTitle" :message="warningModalMessage" type="warning"
      mode="alert" confirmText="Đóng" @confirm="showWarningModal = false" @cancel="showWarningModal = false" />
  </div>
</template>

<script>
import AppToast from './components/AppToast.vue'
import ConfirmModal from './components/ConfirmModal.vue'
import NotificationPanel from './components/common/NotificationPanel.vue'
import { useAuthStore } from './store/auth.store'
import { useSystemStore } from './store/system.store'
import eventBus, { EVENTS } from './utils/eventBus'
import { formatError } from './utils/errorHandler'

export default {
  name: 'App',
  components: { AppToast, ConfirmModal, NotificationPanel },
  data() {
    return {
      // Global Error Modal State
      showErrorModal: false,
      errorModalTitle: 'Lỗi',
      errorModalMessage: '',
      errorModalCode: '',
      errorModalDetails: '',

      // Global Success Modal State
      showSuccessModal: false,
      successModalTitle: 'Thành công',
      successModalMessage: '',

      // Global Warning Modal State
      showWarningModal: false,
      warningModalTitle: 'Cảnh báo',
      warningModalMessage: '',

      authStore: useAuthStore(),
      systemStore: useSystemStore()
    }
  },
  computed: {
    isAuthenticated() { return this.authStore.isAuthenticated },
    isAdmin() { return this.authStore.isAdmin },
    userDisplayName() {
      return this.authStore.user?.profile?.full_name || this.authStore.user?.username || 'User'
    },
    hideNavbar() {
      return ['Login', 'Register'].includes(this.$route.name)
    }
  },
  methods: {
    logout() {
      this.authStore.logout();
      this.$router.push('/login');
    },
    openGlobalError(data) {
      // Handle both old format (error only) and new format ({error, title})
      const error = data?.error || data;
      const title = data?.title || 'Lỗi';

      const { message, errorCode, details } = formatError(error);
      this.errorModalTitle = title;
      this.errorModalMessage = message;
      this.errorModalCode = errorCode;
      this.errorModalDetails = details;
      this.showErrorModal = true;
    },
    closeErrorModal() {
      this.showErrorModal = false;
    },
    openGlobalSuccess(data) {
      if (typeof data === 'string') {
        this.successModalMessage = data;
        this.successModalTitle = 'Thành công';
      } else {
        this.successModalMessage = data.message;
        this.successModalTitle = data.title || 'Thành công';
      }
      this.showSuccessModal = true;
    },
    openGlobalWarning(data) {
      if (typeof data === 'string') {
        this.warningModalMessage = data;
        this.warningModalTitle = 'Cảnh báo';
      } else {
        this.warningModalMessage = data.message;
        this.warningModalTitle = data.title || 'Cảnh báo';
      }
      this.showWarningModal = true;
    }
  },
  mounted() {
    // Tải cấu hình Branding từ server ngay khi app khởi chạy
    this.systemStore.loadFromServer();
    // Subscribe to global error events
    eventBus.on(EVENTS.SHOW_GLOBAL_ERROR, this.openGlobalError);
    eventBus.on(EVENTS.SHOW_GLOBAL_SUCCESS, this.openGlobalSuccess);
    eventBus.on(EVENTS.SHOW_GLOBAL_WARNING, this.openGlobalWarning);
  },
  unmounted() {
    eventBus.off(EVENTS.SHOW_GLOBAL_ERROR, this.openGlobalError);
    eventBus.off(EVENTS.SHOW_GLOBAL_SUCCESS, this.openGlobalSuccess);
    eventBus.off(EVENTS.SHOW_GLOBAL_WARNING, this.openGlobalWarning);
  }
}
</script>

<style>
/* CSS cơ bản cho đẹp */
body {
  margin: 0;
  background-color: #f4f6f8;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

#app {
  text-align: center;
  color: #2c3e50;
}

/* Navbar Styles - Modernized */
.navbar {
  background: v-bind('systemStore.navbarColor');
  padding: 0 1.5rem;
  height: 64px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.brand-icon-wrapper {
  width: 32px;
  height: 32px;
  background: v-bind('systemStore.brandColor');
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.brand-logo-img {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.brand-text {
  font-weight: 800;
  font-size: 1.25rem;
  letter-spacing: -0.02em;
  color: v-bind('systemStore.brandColor');
}

.links {
  display: flex;
  gap: 0.5rem;
  user-select: none;
}

.links a {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: v-bind('systemStore.linkColor');
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  border-radius: 9999px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  cursor: pointer;
}

.links a:hover {
  background: rgba(255, 255, 255, 0.05);
  color: v-bind('systemStore.linkHoverColor');
}

.links a.router-link-active {
  color: v-bind('systemStore.activeLinkColor');
  background: v-bind('systemStore.activeLinkBgColor');
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-profile-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--slate-200);
  transition: all 0.2s;
  cursor: pointer;
  user-select: none;
}

.user-profile-link:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--emerald-500);
  color: white;
}

.user-avatar {
  width: 28px;
  height: 28px;
  background: var(--slate-800);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--emerald-400);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-name {
  font-size: var(--font-sm);
  font-weight: 600;
}

.btn-logout {
  background: transparent;
  color: #ffffff;
  padding: 8px;
  border-radius: 50%;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgb(255, 255, 255);
  color: #000000;
  border-color: rgb(255, 255, 255);
}
</style>
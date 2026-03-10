import { reactive } from 'vue';
import SystemService from '@/services/system.service';

const defaultConfig = {
    brandName: 'AutoContract App',
    logoUrl: '',
    logoType: 'icon',
    navbarColor: '#0f172a',
    brandColor: '#10b981',
    linkColor: '#94a3b8',
    linkHoverColor: '#ffffff',
    activeLinkColor: '#10b981',
    activeLinkBgColor: 'rgba(16, 185, 129, 0.1)'
};

// State reactive - khởi tạo từ giá trị mặc định, sẽ được ghi đè bởi API
const state = reactive({ ...defaultConfig });

// Map: backend snake_case -> frontend camelCase
function mapFromServer(data) {
    return {
        brandName: data.brand_name ?? defaultConfig.brandName,
        logoUrl: data.logo_url ?? defaultConfig.logoUrl,
        logoType: data.logo_url ? 'image' : 'icon',
        navbarColor: data.navbar_color ?? defaultConfig.navbarColor,
        brandColor: data.brand_color ?? defaultConfig.brandColor,
        linkColor: data.link_color ?? defaultConfig.linkColor,
        linkHoverColor: data.link_hover_color ?? defaultConfig.linkHoverColor,
        activeLinkColor: data.active_link_color ?? defaultConfig.activeLinkColor,
        activeLinkBgColor: data.active_link_bg_color ?? defaultConfig.activeLinkBgColor,
    };
}

// Map: frontend camelCase -> backend snake_case
function mapToServer(config) {
    return {
        brand_name: config.brandName,
        logo_url: config.logoUrl,
        navbar_color: config.navbarColor,
        brand_color: config.brandColor,
        link_color: config.linkColor,
        link_hover_color: config.linkHoverColor,
        active_link_color: config.activeLinkColor,
        active_link_bg_color: config.activeLinkBgColor,
    };
}

// Tải cấu hình từ Server (public, không cần đăng nhập)
async function loadFromServer() {
    try {
        const response = await SystemService.getConfig();
        const mapped = mapFromServer(response.data);
        Object.assign(state, mapped);
    } catch (error) {
        console.warn('[SystemConfig] Không thể tải cấu hình từ server, dùng giá trị mặc định.', error);
        // Fallback: giữ nguyên defaultConfig
    }
}

// Lưu cấu hình lên Server (admin-only) - cũng cập nhật state local ngay lập tức
async function updateConfig(newConfig) {
    // Cập nhật state local ngay để UI phản hồi tức thì
    Object.assign(state, newConfig);

    // Đồng bộ lên server
    try {
        const payload = mapToServer(state);
        await SystemService.updateConfig(payload);
    } catch (error) {
        console.error('[SystemConfig] Không thể lưu cấu hình lên server.', error);
        throw error; // Ném lỗi để AdminSettings.vue xử lý thông báo
    }
}

// Upload logo lên server, sau đó cập nhật logoUrl trong DB
async function uploadLogo(file) {
    const formData = new FormData();
    formData.append('logo', file);

    const response = await SystemService.uploadLogo(formData);

    if (response.data.logoUrl) {
        await updateConfig({ logoUrl: response.data.logoUrl, logoType: 'image' });
    }
    return response.data;
}

// Đặt lại về mặc định - cả server lẫn state
async function resetToDefault() {
    Object.assign(state, defaultConfig);
    try {
        const payload = mapToServer(defaultConfig);
        await SystemService.updateConfig(payload);
    } catch (error) {
        console.error('[SystemConfig] Không thể reset cấu hình trên server.', error);
    }
}

export default {
    state,
    loadFromServer,
    updateConfig,
    resetToDefault,
    uploadLogo
};

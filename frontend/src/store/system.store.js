import { defineStore } from 'pinia';
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
    activeLinkBgColor: 'rgba(16, 185, 129, 0.1)',
    autoSaveEnabled: true
};

export const useSystemStore = defineStore('system', {
    state: () => ({
        ...defaultConfig,
        objectTypes: [],
        allFields: [],
        isLoading: false
    }),

    actions: {
        // Map: backend snake_case -> frontend camelCase
        mapFromServer(data) {
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
                autoSaveEnabled: data.auto_save_enabled ?? defaultConfig.autoSaveEnabled,
            };
        },

        // Map: frontend camelCase -> backend snake_case
        mapToServer(config) {
            return {
                brand_name: config.brandName,
                logo_url: config.logoUrl,
                navbar_color: config.navbarColor,
                brand_color: config.brandColor,
                link_color: config.linkColor,
                link_hover_color: config.linkHoverColor,
                active_link_color: config.activeLinkColor,
                active_link_bg_color: config.activeLinkBgColor,
                auto_save_enabled: config.autoSaveEnabled,
            };
        },

        async loadFromServer() {
            try {
                const response = await SystemService.getConfig();
                const mapped = this.mapFromServer(response.data);
                Object.assign(this.$state, mapped);
            } catch (error) {
                console.warn('[SystemStore] Không thể tải cấu hình từ server, dùng giá trị mặc định.', error);
            }
        },

        async updateConfig(newConfig) {
            Object.assign(this.$state, newConfig);
            try {
                const payload = this.mapToServer(this.$state);
                await SystemService.updateConfig(payload);
            } catch (error) {
                console.error('[SystemStore] Không thể lưu cấu hình lên server.', error);
                throw error;
            }
        },

        async uploadLogo(file) {
            const formData = new FormData();
            formData.append('logo', file);
            const response = await SystemService.uploadLogo(formData);
            if (response.data.logoUrl) {
                await this.updateConfig({ logoUrl: response.data.logoUrl, logoType: 'image' });
            }
            return response.data;
        },

        async resetToDefault() {
            Object.assign(this.$state, { ...defaultConfig, objectTypes: this.objectTypes, allFields: this.allFields });
            try {
                const payload = this.mapToServer(defaultConfig);
                await SystemService.updateConfig(payload);
            } catch (error) {
                console.error('[SystemStore] Không thể reset cấu hình trên server.', error);
            }
        }
    }
});

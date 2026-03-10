<template>
    <div class="admin-page">
        <div class="admin-form-grid">
            <section class="admin-form-section">
                <h4>Tùy chỉnh Thương hiệu</h4>

                <div class="admin-field">
                    <label>Tên ứng dụng (Brand Name)</label>
                    <input type="text" v-model="editConfig.brandName" class="admin-form-control"
                        placeholder="Nhập tên ứng dụng..." />
                </div>

                <div class="admin-field">
                    <label>Loại Logo</label>
                    <div class="field-row">
                        <label class="admin-radio-label">
                            <input type="radio" v-model="editConfig.logoType" value="icon" /> Icon mặc định
                        </label>
                        <label class="admin-radio-label ml-4">
                            <input type="radio" v-model="editConfig.logoType" value="image" /> Ảnh tùy chỉnh
                        </label>
                    </div>
                </div>

                <div class="admin-field">
                    <label>Logo hiển thị</label>
                    <div class="logo-upload-zone">
                        <div class="upload-controls">
                            <input type="file" ref="logoInput" @change="handleLogoUpload" accept="image/*"
                                style="display: none" />
                            <button class="btn-action btn-secondary" @click="$refs.logoInput.click()"
                                :disabled="uploading || !auth.isSuperuser"
                                :title="!auth.isSuperuser ? 'Chỉ quản trị viên cấp cao (Root) mới được thay đổi Logo' : 'Tải lên Logo mới'">
                                <SvgIcon :name="uploading ? 'refresh' : 'upload'" size="sm"
                                    :customClass="uploading ? 'spin' : ''" />
                                {{ uploading ? 'Đang tải...' : 'Tải lên Logo mới' }}
                            </button>
                        </div>

                        <div class="url-fallback">
                            <span>Hoặc URL ảnh:</span>
                            <input type="text" v-model="editConfig.logoUrl" class="admin-form-control"
                                placeholder="Dán link ảnh tại đây..." />
                        </div>
                    </div>
                    <p class="hint">Khuyên dùng ảnh PNG trong suốt hoặc SVG dưới 2MB. Logo sẽ được lưu trữ an toàn trên
                        server.</p>
                </div>

                <div class="color-settings-grid">
                    <div class="admin-field">
                        <label>Màu thanh điều hướng</label>
                        <div class="color-picker-wrapper">
                            <input type="color" v-model="editConfig.navbarColor" class="admin-color-control" />
                            <span class="color-code">{{ editConfig.navbarColor }}</span>
                        </div>
                    </div>

                    <div class="admin-field">
                        <label>Màu Thương hiệu</label>
                        <div class="color-picker-wrapper">
                            <input type="color" v-model="editConfig.brandColor" class="admin-color-control" />
                            <span class="color-code">{{ editConfig.brandColor }}</span>
                        </div>
                    </div>

                    <div class="admin-field">
                        <label>Màu Link (Thường)</label>
                        <div class="color-picker-wrapper">
                            <input type="color" v-model="editConfig.linkColor" class="admin-color-control" />
                            <span class="color-code">{{ editConfig.linkColor }}</span>
                        </div>
                    </div>

                    <div class="admin-field">
                        <label>Màu Link (Hover)</label>
                        <div class="color-picker-wrapper">
                            <input type="color" v-model="editConfig.linkHoverColor" class="admin-color-control" />
                            <span class="color-code">{{ editConfig.linkHoverColor }}</span>
                        </div>
                    </div>

                    <div class="admin-field">
                        <label>Màu Link (Active)</label>
                        <div class="color-picker-wrapper">
                            <input type="color" v-model="editConfig.activeLinkColor" class="admin-color-control" />
                            <span class="color-code">{{ editConfig.activeLinkColor }}</span>
                        </div>
                    </div>

                    <div class="admin-field">
                        <label>Màu nền Link (Active)</label>
                        <div class="color-picker-wrapper">
                            <input type="color" v-model="editConfig.activeLinkBgColor" class="admin-color-control" />
                            <span class="color-code">{{ editConfig.activeLinkBgColor }}</span>
                        </div>
                    </div>
                </div>

                <div class="preview-section" :style="{ background: editConfig.navbarColor }">
                    <label>Xem trước Branding</label>
                    <div class="branding-preview">
                        <div class="preview-logo">
                            <img v-if="editConfig.logoType === 'image' && editConfig.logoUrl" :src="editConfig.logoUrl"
                                alt="Preview" />
                            <div v-else class="preview-icon" :style="{ background: editConfig.brandColor }">
                                <SvgIcon name="layers" size="md" />
                            </div>
                        </div>
                        <span class="preview-text" :style="{ color: editConfig.brandColor }">
                            {{ editConfig.brandName }}
                        </span>
                    </div>
                    <div class="links-preview">
                        <span :style="{ color: editConfig.linkColor }">Liên kết mẫu</span>
                        <span
                            :style="{ color: editConfig.linkHoverColor, background: 'rgba(255,255,255,0.1)', padding: '4px 12px', borderRadius: '999px' }">Hover
                            mẫu</span>
                        <span
                            :style="{ color: editConfig.activeLinkColor, background: editConfig.activeLinkBgColor, padding: '4px 12px', borderRadius: '999px', position: 'relative' }">
                            Active mẫu
                        </span>
                    </div>
                </div>

                <div class="settings-actions">
                    <button @click="saveChanges" class="btn-action btn-save"
                        :disabled="!isChanged || uploading || !auth.isSuperuser"
                        :title="!auth.isSuperuser ? 'Chỉ quản trị viên cấp cao (Root) mới được thay đổi cấu hình' : 'Lưu cấu hình'">
                        <SvgIcon name="save" size="sm" /> Lưu cấu hình
                    </button>
                    <button @click="resetToDefault" class="btn-action btn-secondary ml-2"
                        :disabled="uploading || !auth.isSuperuser"
                        :title="!auth.isSuperuser ? 'Chỉ quản trị viên cấp cao (Root) mới được khôi phục mặc định' : 'Khôi phục mặc định'">
                        <SvgIcon name="refresh" size="sm" /> Khôi phục mặc định
                    </button>
                </div>
            </section>

            <section class="admin-form-section">
                <h4>Hướng dẫn & Mẹo</h4>
                <ul class="settings-tips">
                    <li><strong>Brand Name:</strong> Xuất hiện trên thanh Navbar và tiêu đề trình duyệt.</li>
                    <li><strong>Upload Logo:</strong> File của bạn sẽ được tải lên máy chủ và đổi tên an toàn. Điều này
                        giúp logo không bị mất khi dán link ngoài.</li>
                    <li><strong>Màu sắc:</strong> Bạn có thể tùy chỉnh toàn bộ tông màu của thanh điều hướng để phù hợp
                        với bộ nhận diện thương hiệu.</li>
                </ul>
            </section>
        </div>
    </div>
</template>

<script>
import systemConfig from '@/store/systemConfig';
import auth from '@/store/auth';
import SvgIcon from '@/components/common/SvgIcon.vue';

export default {
    name: 'AdminSettings',
    title: 'Cài đặt hệ thống',
    components: { SvgIcon },
    data() {
        return {
            uploading: false,
            editConfig: {
                brandName: systemConfig.state.brandName,
                logoUrl: systemConfig.state.logoUrl,
                logoType: systemConfig.state.logoType,
                navbarColor: systemConfig.state.navbarColor,
                brandColor: systemConfig.state.brandColor,
                linkColor: systemConfig.state.linkColor,
                linkHoverColor: systemConfig.state.linkHoverColor,
                activeLinkColor: systemConfig.state.activeLinkColor,
                activeLinkBgColor: systemConfig.state.activeLinkBgColor
            },
            auth
        };
    },
    computed: {
        isChanged() {
            return this.editConfig.brandName !== systemConfig.state.brandName ||
                this.editConfig.logoUrl !== systemConfig.state.logoUrl ||
                this.editConfig.logoType !== systemConfig.state.logoType ||
                this.editConfig.navbarColor !== systemConfig.state.navbarColor ||
                this.editConfig.brandColor !== systemConfig.state.brandColor ||
                this.editConfig.linkColor !== systemConfig.state.linkColor ||
                this.editConfig.linkHoverColor !== systemConfig.state.linkHoverColor ||
                this.editConfig.activeLinkColor !== systemConfig.state.activeLinkColor ||
                this.editConfig.activeLinkBgColor !== systemConfig.state.activeLinkBgColor;
        }
    },
    methods: {
        async handleLogoUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Validate client-side cơ bản
            if (!file.type.startsWith('image/')) {
                this.$toast.error('Vui lòng chọn file ảnh hợp lệ.');
                return;
            }
            if (file.size > 2 * 1024 * 1024) {
                this.$toast.error('File không được vượt quá 2MB.');
                return;
            }

            this.uploading = true;
            try {
                const result = await systemConfig.uploadLogo(file);
                this.editConfig.logoUrl = result.logoUrl;
                this.editConfig.logoType = 'image';
                this.$toast.success('Đã tải logo lên máy chủ thành công!');
            } catch (error) {
                console.error('Upload error:', error);
                const errorMsg = error.response?.data?.error || 'Có lỗi xảy ra khi tải logo.';
                this.$toast.error(errorMsg);
            } finally {
                this.uploading = false;
                // Reset input file để có thể chọn lại cùng 1 file
                if (this.$refs.logoInput) this.$refs.logoInput.value = '';
            }
        },
        async saveChanges() {
            try {
                await systemConfig.updateConfig(this.editConfig);
                this.$toast.success('Đã lưu cấu hình lên máy chủ thành công!');
            } catch (error) {
                const msg = error.response?.data?.detail || error.message || 'Có lỗi xảy ra khi lưu cấu hình.';
                this.$toast.error(msg);
            }
        },
        async resetToDefault() {
            if (confirm('Bạn có chắc chắn muốn khôi phục về cấu hình mặc định?')) {
                try {
                    await systemConfig.resetToDefault();
                    this.editConfig = { ...systemConfig.state };
                    this.$toast.info('Đã khôi phục cài đặt mặc định.');
                } catch (error) {
                    this.$toast.error('Không thể khôi phục mặc định. Vui lòng thử lại.');
                }
            }
        }
    }
};
</script>

<style scoped>
/* .admin-page padding is now global in admin.css */

.color-settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.logo-upload-zone {
    background: var(--slate-50);
    border: 1px dashed var(--slate-300);
    border-radius: 8px;
    padding: 16px;
    margin-top: 8px;
}

.upload-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.url-fallback {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: var(--font-xs);
    color: var(--slate-500);
    border-top: 1px solid var(--slate-200);
    padding-top: 12px;
}

.url-fallback span {
    white-space: nowrap;
}

.preview-section {
    margin-top: 30px;
    padding: 30px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.preview-section label {
    color: rgba(255, 255, 255, 0.5);
    font-size: var(--font-xs);
    margin-bottom: 20px;
    display: block;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.branding-preview {
    display: flex;
    align-items: center;
    gap: 16px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-logo img {
    height: 40px;
    width: auto;
}

.preview-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.preview-text {
    font-weight: 800;
    font-size: 1.5rem;
    letter-spacing: -0.02em;
}

.links-preview {
    margin-top: 20px;
    display: flex;
    gap: 20px;
    align-items: center;
    font-size: 0.9rem;
}

.color-picker-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 8px;
}

.admin-color-control {
    width: 40px;
    height: 32px;
    padding: 0;
    border: none;
    cursor: pointer;
    background: none;
}

.color-code {
    font-family: monospace;
    font-size: 0.8rem;
    color: var(--slate-600);
    background: var(--slate-200);
    padding: 2px 6px;
    border-radius: 4px;
}

.hint {
    font-size: 0.75rem;
    color: var(--slate-500);
    margin-top: 8px;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.spin {
    animation: spin 1s linear infinite;
}
</style>

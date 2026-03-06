<template>
    <vxe-modal v-model="visibleProxy" :title="item ? 'Chỉnh sửa Thông báo' : 'Tạo Thông báo mới'" width="600"
        show-footer @close="$emit('close')">
        <div class="notification-form">
            <div class="form-group">
                <label>Tiêu đề <span class="required">*</span></label>
                <vxe-input v-model="formData.title" placeholder="Nhập tiêu đề thông báo" clearable
                    class="input-title"></vxe-input>
            </div>

            <div class="form-row">
                <div class="form-group half">
                    <label>Loại thông báo</label>
                    <vxe-select v-model="formData.type" class="select-type">
                        <vxe-option value="INFO" label="Thông tin (Xanh)"></vxe-option>
                        <vxe-option value="WARN" label="Cảnh báo (Vàng)"></vxe-option>
                        <vxe-option value="DANGER" label="Khẩn cấp (Đỏ)"></vxe-option>
                    </vxe-select>
                </div>
                <div class="form-group half">
                    <label>Ngày hết hạn (Tuỳ chọn)</label>
                    <vxe-input v-model="formData.expires_at" type="datetime" placeholder="Để trống nếu không giới hạn"
                        clearable class="input-expires"></vxe-input>
                </div>
            </div>

            <div class="form-group">
                <label>Nội dung <span class="required">*</span></label>
                <vxe-textarea v-model="formData.content" placeholder="Nhập nội dung thông báo..."
                    :autosize="{ minRows: 4, maxRows: 8 }" class="textarea-content"></vxe-textarea>
            </div>
        </div>

        <template #footer>
            <button @click="$emit('close')" class="btn-action">Hủy</button>
            <button @click="save" class="btn-action btn-primary" :disabled="loading">
                <SvgIcon v-if="loading" name="loading" size="sm" class="spinning" />
                {{ item ? 'Cập nhật' : 'Lưu & Đẩy' }}
            </button>
        </template>
    </vxe-modal>
</template>

<script>
import axios from 'axios';
import SvgIcon from '@/components/common/SvgIcon.vue';
import { API_URL } from '@/store/auth';

export default {
    name: 'NotificationEditModal',
    components: { SvgIcon },
    props: {
        visible: Boolean,
        item: Object
    },
    emits: ['close', 'saved'],
    data() {
        return {
            loading: false,
            formData: {
                title: '',
                content: '',
                type: 'INFO',
                expires_at: null,
                is_active: true
            }
        };
    },
    computed: {
        visibleProxy: {
            get() { return this.visible; },
            set(val) { if (!val) this.$emit('close'); }
        }
    },
    watch: {
        item: {
            immediate: true,
            handler(newVal) {
                if (newVal) {
                    this.formData = { ...newVal };
                } else {
                    this.formData = { title: '', content: '', type: 'INFO', expires_at: null, is_active: true };
                }
            }
        }
    },
    methods: {
        async save() {
            if (!this.formData.title || !this.formData.content) {
                this.$toast.warning('Vui lòng nhập đầy đủ tiêu đề và nội dung');
                return;
            }

            this.loading = true;
            try {
                if (this.item) {
                    await axios.put(`${API_URL}/notifications/${this.item.id}/`, this.formData);
                    this.$toast.success('Đã cập nhật thông báo');
                } else {
                    await axios.post(`${API_URL}/notifications/`, this.formData);
                    this.$toast.success('Đã đẩy thông báo tới toàn bộ người dùng');
                }
                this.$emit('saved');
                this.$emit('close');
            } catch (err) {
                this.$toast.error('Lỗi khi lưu thông báo');
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>

<style scoped>
.notification-form {
    padding: 10px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    font-size: 0.9rem;
}

.form-row {
    display: flex;
    gap: 15px;
}

.half {
    flex: 1;
}

.required {
    color: #ff4d4f;
}

.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.glass-effect {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Tùy chỉnh độ rộng các input */
.input-title {
    width: 100%;
    /* Bạn có thể chỉnh thành px hoặc % cụ thể */
}

.select-type {
    width: 100%;
}

.input-expires {
    width: 100%;
}

.textarea-content {
    width: 100%;
}
</style>

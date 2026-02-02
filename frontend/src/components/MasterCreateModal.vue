<template>
    <BaseModal :isOpen="isOpen" :title="title" @close="close">
        <div class="sync-note">
            <span class="icon">ℹ️</span>
            Khi cập nhật, thông tin mới chỉ được áp dụng cho các hồ sơ nháp. Các hồ sơ đã khóa không bị
            ảnh hưởng.
        </div>
        <div v-if="loadingFields" class="loading-state">Đang tải cấu hình trường...</div>
        <div v-else>
            <div v-for="(fields, groupName) in groupedFields" :key="groupName" class="admin-form-section">
                <h4>{{ groupName }}</h4>
                <DynamicForm :fields="fields" v-model="formData" inputClass="admin-input" />
            </div>
        </div>

        <template #footer>
            <button class="btn-action btn-secondary" @click="close">Hủy</button>
            <button class="btn-action btn-primary" @click="handleSave" :disabled="isSaving">
                {{ isSaving ? 'Đang lưu...' : (isEdit ? 'Cập nhật' : 'Tạo mới') }}
            </button>
        </template>
    </BaseModal>
</template>

<script>
import axios from 'axios';
import DynamicForm from './DynamicForm.vue';
import BaseModal from './BaseModal.vue';

export default {
    name: 'MasterCreateModal',
    components: { DynamicForm, BaseModal },
    props: {
        isOpen: Boolean,
        type: String, // 'PERSON', 'ASSET', 'SAVINGS'
        typeName: { type: String, default: 'Đối tượng' },
        editObject: Object // Null if creating
    },
    emits: ['close', 'success'],
    data() {
        return {
            loadingFields: false,
            isSaving: false,
            allFields: [],
            formData: {}
        };
    },
    computed: {
        isEdit() {
            return !!this.editObject;
        },
        title() {
            const action = this.isEdit ? 'Cập nhật' : 'Thêm mới';
            return `${action} ${this.typeName}`;
        },
        groupedFields() {
            const groups = {};
            this.allFields.forEach(field => {
                const gName = field.group_name || 'Thông tin chung';
                if (!groups[gName]) groups[gName] = [];
                groups[gName].push(field);
            });
            return groups;
        }
    },
    watch: {
        isOpen: {
            handler(val) {
                if (val) {
                    this.initModal();
                }
            },
            immediate: true
        },

        editObject: {
            handler() {
                if (this.isOpen) {
                    this.initModal();
                }
            },
            deep: true
        },

        type: {
            handler() {
                if (this.isOpen) {
                    this.initModal();
                }
            }
        }

    },
    methods: {
        initModal() {
            if (this.isEdit) {
                this.formData = { ...this.editObject.field_values };
            } else {
                this.formData = {};
            }
            this.fetchFields();
        },
        async fetchFields() {
            this.loadingFields = true;
            try {
                // Sử dụng API active_fields_grouped với entity_type mới
                const res = await axios.get(`http://127.0.0.1:8000/api/fields/active_fields_grouped/?entity_type=${this.type}`);

                // Flatten the grouped result from API into a simple array for DynamicForm if needed
                const flatFields = [];
                Object.keys(res.data).forEach(groupName => {
                    res.data[groupName].forEach(field => {
                        flatFields.push({ ...field, group_name: groupName });
                    });
                });
                this.allFields = flatFields;

                // Apply defaults if creating
                if (!this.isEdit) {
                    const defaults = {};
                    this.allFields.forEach(f => {
                        if (f.default_value) defaults[f.placeholder_key] = f.default_value;
                    });
                    this.formData = defaults;
                }
            } catch (error) {
                console.error('Lỗi khi tải fields cho master data:', error);
            } finally {
                this.loadingFields = false;
            }
        },
        async handleSave() {
            this.isSaving = true;
            try {
                const payload = {
                    object_type: this.type,
                    field_values: this.formData
                };

                if (this.isEdit) {
                    await axios.patch(`http://127.0.0.1:8000/api/master-objects/${this.editObject.id}/`, payload);
                } else {
                    await axios.post(`http://127.0.0.1:8000/api/master-objects/`, payload);
                }

                this.$toast.success(`${this.isEdit ? 'Cập nhật' : 'Tạo mới'} thành công!`);
                this.$emit('success');
                this.close();
            } catch (error) {
                console.error('Lỗi khi lưu master data:', error);
                const data = error.response?.data;
                if (data && data.code === 'duplicate') {
                    this.$toast.warning('LỖI: ' + data.message);
                } else if (data && data.message) {
                    this.$toast.error('Lỗi: ' + data.message);
                } else {
                    this.$toast.error('Không thể lưu dữ liệu. Có thể do trùng lặp hoặc lỗi hệ thống.');
                }
            } finally {
                this.isSaving = false;
            }
        },

        close() {
            this.$emit('close');
        }
    }
};
</script>

<style scoped>
.sync-note {
    background: #e8f4fd;
    border-left: 4px solid #3498db;
    padding: 12px 15px;
    margin-bottom: 25px;
    border-radius: 4px;
    font-size: 0.9rem;
    color: #2980b9;
    display: flex;
    align-items: center;
    gap: 10px;
    line-height: 1.4;
}

.sync-note .icon {
    font-size: 1.2rem;
}

.loading-state {
    text-align: center;
    padding: 60px;
    color: #95a5a6;
    font-style: italic;
}
</style>

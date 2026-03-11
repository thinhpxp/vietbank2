<template>
    <BaseModal :isOpen="isOpen" :title="title" :initialWidth="1100" :isResizable="true" @close="close">
        <div class="info-box info">
            <div class="info-box-icon">
                <SvgIcon name="info" size="sm" />
            </div>
            <div class="info-box-content">
                Khi cập nhật, thông tin mới chỉ được áp dụng cho các hồ sơ nháp. Các hồ sơ đã khóa không bị ảnh hưởng.
            </div>
        </div>
        <div v-if="loadingFields" class="loading-state">Đang tải cấu hình trường...</div>
        <div v-else>
            <div v-for="(fields, groupName) in groupedFields" :key="groupName" class="admin-form-section">
                <h4>{{ groupName }}</h4>
                <DynamicForm :fields="fields" v-model="formData" :disabled="readOnly" inputClass="admin-input" />
            </div>
        </div>

        <template #footer>
            <div v-if="readOnly" class="text-warning text-sm mr-auto font-bold flex items-center gap-2">
                <SvgIcon name="alert" size="sm" />
                <span>Bạn hiện chỉ xem được thông tin, vì người khác đang chỉnh sửa đối tượng này</span>
            </div>
            <button class="btn-action btn-secondary" @click="close">Hủy</button>
            <button v-if="!readOnly" class="btn-action btn-save" @click="handleSave" :disabled="isSaving">
                {{ isSaving ? 'Đang lưu...' : (isEdit ? 'Cập nhật' : 'Tạo mới') }}
            </button>
        </template>
    </BaseModal>
</template>

<script>
import MasterService from '@/services/master.service';
import DynamicForm from './DynamicForm.vue';
import BaseModal from './BaseModal.vue';
import SvgIcon from './common/SvgIcon.vue';

export default {
    name: 'MasterCreateModal',
    components: { DynamicForm, BaseModal, SvgIcon },
    props: {
        isOpen: Boolean,
        type: String, // 'PERSON', 'ASSET', 'SAVINGS'
        typeName: { type: String, default: 'Đối tượng' },
        editObject: Object, // Null if creating
        readOnly: { type: Boolean, default: false }
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
            const action = this.readOnly ? 'Xem thông tin' : (this.isEdit ? 'Cập nhật' : 'Thêm mới');
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
                const res = await MasterService.getFieldsGrouped(this.type);

                // Flatten the grouped result from API into a simple array for DynamicForm if needed
                const flatFields = [];
                if (res && res.data) {
                    Object.keys(res.data).forEach(groupName => {
                        if (Array.isArray(res.data[groupName])) {
                            res.data[groupName].forEach(field => {
                                flatFields.push({ ...field, group_name: groupName });
                            });
                        }
                    });
                }
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
                    await MasterService.updateObject(this.editObject.id, payload);
                } else {
                    await MasterService.createObject(payload);
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
/* Standardized styles are now using global classes from common-ui.css / admin.css */
</style>

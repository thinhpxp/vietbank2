<template>
    <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <div class="modal-content side-modal">
            <div class="modal-header">
                <h3>{{ title }}</h3>
                <button class="btn-close" @click="close">&times;</button>
            </div>
            <div class="modal-body">
                <div v-if="loadingFields" class="loading-state">Đang tải cấu hình trường...</div>
                <div v-else>
                    <div v-for="(fields, groupName) in groupedFields" :key="groupName" class="section-container">
                        <h4 class="section-title">{{ groupName }}</h4>
                        <DynamicForm :fields="fields" v-model="formData" />
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-cancel" @click="close">Hủy</button>
                <button class="btn-save" @click="handleSave" :disabled="isSaving">
                    {{ isSaving ? 'Đang lưu...' : (isEdit ? 'Cập nhật' : 'Tạo mới') }}
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import DynamicForm from './DynamicForm.vue';

export default {
    name: 'MasterCreateModal',
    components: { DynamicForm },
    props: {
        isOpen: Boolean,
        type: String, // 'PERSON', 'ASSET', 'SAVINGS'
        typeName: { type: String, default: 'Đối tượng' },
        editObject: Object // Null if creating
    },
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
        isOpen(val) {
            if (val) {
                this.fetchFields();
                if (this.isEdit) {
                    this.formData = { ...this.editObject.field_values };
                } else {
                    this.formData = {};
                }
            }
        }
    },
    methods: {
        async fetchFields() {
            this.loadingFields = true;
            try {
                // Sử dụng API active_fields_grouped với entity_type mới
                const res = await axios.get(`http://127.0.0.1:8000/api/fields/active_fields_grouped/?entity_type=${this.type}`);

                // Flatten the grouped result from API into a simple array for DynamicForm if needed
                // OR adapt to how MasterData wants it. 
                // views.py returns: { "Group Name": [field1, field2] }
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
                    object_type: this.type, // PERSON, ASSET, etc.
                    field_values: this.formData
                };

                if (this.isEdit) {
                    await axios.patch(`http://127.0.0.1:8000/api/master-objects/${this.editObject.id}/`, payload);
                } else {
                    await axios.post(`http://127.0.0.1:8000/api/master-objects/`, payload);
                }

                this.$emit('success');
                this.close();
            } catch (error) {
                console.error('Lỗi khi lưu master data:', error);
                const data = error.response?.data;
                if (data && data.code === 'duplicate') {
                    alert('LỐI: ' + data.message);
                } else if (data && data.message) {
                    alert('Lỗi: ' + data.message);
                } else {
                    alert('Không thể lưu dữ liệu. Có thể do trùng lặp hoặc lỗi hệ thống.');
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
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: flex-end;
    z-index: 2100;
}

.modal-content.side-modal {
    background: white;
    width: 500px;
    height: 100%;
    display: flex;
    flex-direction: column;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.2);
}

.modal-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8f9fa;
}

.modal-body {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
}

.modal-footer {
    padding: 15px 20px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    background: #f8f9fa;
}

.section-container {
    margin-bottom: 25px;
}

.section-title {
    margin-bottom: 15px;
    padding-bottom: 5px;
    border-bottom: 2px solid #3498db;
    color: #2c3e50;
    font-size: 1.1rem;
}

.btn-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
}

.btn-cancel {
    padding: 8px 15px;
    background: #e9ecef;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

.btn-save {
    padding: 8px 25px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.btn-save:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
}

.loading-state {
    text-align: center;
    padding: 40px;
    color: #666;
}
</style>

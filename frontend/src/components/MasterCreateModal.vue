<template>
    <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <div class="modal-content popup-modal">
            <div class="modal-header">
                <h3>{{ title }}</h3>
                <button class="btn-close" @click="close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="sync-note">
                    <span class="icon">ℹ️</span> 
                    Thông tin mới chỉ được áp dụng cho các hồ sơ nháp, các hồ sơ đã hoàn tất/khóa không bị ảnh hưởng.
                </div>
                <div v-if="loadingFields" class="loading-state">Đang tải cấu hình trường...</div>
                <div v-else>
                    <div v-for="(fields, groupName) in groupedFields" :key="groupName" class="section-container">
                        <h4 class="section-title">{{ groupName }}</h4>
                        <DynamicForm :fields="fields" v-model="formData" inputClass="admin-input" />
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
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2500;
}

.modal-content.popup-modal {
    background: white;
    width: 650px;
    max-width: 95%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    border-radius: 12px;
    overflow: hidden;
    animation: modalAppear 0.3s ease-out;
}

@keyframes modalAppear {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.modal-header {
    padding: 20px 25px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fcfcfc;
}

.modal-header h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.25rem;
}

.modal-body {
    flex: 1;
    padding: 25px;
    overflow-y: auto;
}

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

.modal-footer {
    padding: 15px 25px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    background: #f8f9fa;
}

.section-container {
    margin-bottom: 30px;
}

.section-title {
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #3498db;
    color: #34495e;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.btn-close {
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #bdc3c7;
    transition: color 0.2s;
    line-height: 1;
}

.btn-close:hover {
    color: #e74c3c;
}

.btn-cancel {
    padding: 10px 20px;
    background: white;
    border: 1px solid #dcdfe6;
    border-radius: 6px;
    cursor: pointer;
    color: #606266;
    font-weight: 500;
    transition: all 0.2s;
}

.btn-cancel:hover {
    background: #f5f7fa;
    border-color: #c0c4cc;
}

.btn-save {
    padding: 10px 30px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.2s;
    box-shadow: 0 4px 6px rgba(52, 152, 219, 0.2);
}

.btn-save:hover {
    background: #2980b9;
}

.btn-save:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    box-shadow: none;
}

.loading-state {
    text-align: center;
    padding: 60px;
    color: #95a5a6;
    font-style: italic;
}
</style>

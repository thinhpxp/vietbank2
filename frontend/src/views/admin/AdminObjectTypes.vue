<template>
    <div class="admin-page dashboard-container">
        <div class="header-actions">
            <h2>Quản lý Loại Đối tượng (Object Types)</h2>
            <button class="btn-action btn-create" @click="openCreateModal">+ Thêm Loại mới</button>
        </div>

        <table class="data-table">
            <thead>
                <tr>
                    <th>Mã (Code)</th>
                    <th>Tên hiển thị</th>
                    <th>Trường định danh (key)</th>
                    <th>Mô tả</th>
                    <th>Hệ thống</th>
                    <th>Hành động</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="type in types" :key="type.id">
                    <td><code>{{ type.code }}</code></td>
                    <td class="font-bold">{{ type.name }}</td>
                    <td><code>{{ type.identity_field_key || '---' }}</code></td>
                    <td>{{ type.description || '---' }}</td>
                    <td>
                        <span v-if="type.is_system" class="badge badge-system">System</span>
                        <span v-else class="badge badge-custom">Custom</span>
                    </td>
                    <td>
                        <div class="action-group">
                            <button class="btn-action btn-edit" @click="editType(type)">Sửa</button>
                            <button class="btn-action btn-delete" :disabled="type.is_system"
                                @click="confirmDelete(type)"
                                :title="type.is_system ? 'Không thể xóa loại mặc định' : 'Xóa loại này'">
                                Xóa
                            </button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>

        <!-- Modal Create/Edit -->
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal-content side-modal">
                <div class="modal-header">
                    <h3>{{ isEdit ? 'Cập nhật Loại' : 'Thêm Loại mới' }}</h3>
                    <button class="btn-close" @click="closeModal">&times;</button>
                </div>

                <div class="modal-body">
                    <div class="form-group">
                        <label>Mã loại (Code) *</label>
                        <input v-model="formData.code" :disabled="isEdit" placeholder="VD: PROJECT" class="admin-input"
                            style="width: 100%" />
                        <small class="hint">Viết hoa, không dấu, không khoảng trắng.</small>
                    </div>

                    <div class="form-group">
                        <label>Tên hiển thị *</label>
                        <input v-model="formData.name" placeholder="VD: Dự án" class="admin-input"
                            style="width: 100%" />
                    </div>

                    <div class="form-group">
                        <label>Trường định danh (key)</label>
                        <input v-model="formData.identity_field_key" placeholder="VD: ho_ten, bien_so_xe"
                            class="admin-input" style="width: 100%" />
                        <small class="hint">Tên trường dùng để định danh cho đối tượng này.</small>
                    </div>

                    <div class="form-group">
                        <label>Mô tả</label>
                        <textarea v-model="formData.description" class="admin-input" rows="3"
                            style="width: 100%; min-height: 80px;"></textarea>
                    </div>

                    <div class="modal-footer"
                        style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                        <button class="btn-action btn-secondary" @click="closeModal">Hủy</button>
                        <button class="btn-action btn-save" @click="saveType">Lưu</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Confirm Delete -->
        <ConfirmModal :visible="showDeleteModal" title="Xóa Loại đối tượng"
            :message="`Bạn có chắc muốn xóa loại '${deleteTarget?.name}'? Các dữ liệu thuộc loại này có thể bị ảnh hưởng.`"
            confirmText="Xóa ngay" @confirm="executeDelete" @cancel="showDeleteModal = false" />
    </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { makeTableResizable } from '../../utils/resizable-table';

export default {
    name: 'AdminObjectTypes',
    components: { ConfirmModal },
    data() {
        return {
            types: [],
            showModal: false,
            isEdit: false,
            formData: { code: '', name: '', description: '' },
            showDeleteModal: false,
            deleteTarget: null
        };
    },
    mounted() {
        this.fetchTypes();
        this.initResizable();
    },
    methods: {
        async fetchTypes() {
            try {
                const res = await axios.get('http://127.0.0.1:8000/api/object-types/');
                this.types = res.data;
                this.$nextTick(() => this.initResizable());
            } catch (e) {
                console.error(e);
            }
        },
        initResizable() {
            const table = this.$el.querySelector('.data-table');
            if (table) {
                makeTableResizable(table, 'admin-object-types');
            }
        },
        openCreateModal() {
            this.isEdit = false;
            this.formData = { code: '', name: '', description: '', identity_field_key: '' };
            this.showModal = true;
        },
        editType(item) {
            this.isEdit = true;
            this.formData = { ...item };
            this.showModal = true;
        },
        closeModal() {
            this.showModal = false;
        },
        async saveType() {
            if (!this.formData.code || !this.formData.name) return alert('Vui lòng nhập Mã và Tên');

            try {
                if (this.isEdit) {
                    await axios.patch(`http://127.0.0.1:8000/api/object-types/${this.formData.id}/`, this.formData);
                } else {
                    await axios.post('http://127.0.0.1:8000/api/object-types/', this.formData);
                }
                this.fetchTypes();
                this.closeModal();
            } catch (e) {
                alert('Lỗi khi lưu (Có thể mã đã tồn tại)');
                console.error(e);
            }
        },
        confirmDelete(item) {
            this.deleteTarget = item;
            this.showDeleteModal = true;
        },
        async executeDelete() {
            try {
                await axios.delete(`http://127.0.0.1:8000/api/object-types/${this.deleteTarget.id}/`);
                this.fetchTypes();
                this.showDeleteModal = false;
            } catch (e) {
                alert('Lỗi xóa');
            }
        }
    }
};
</script>

<style scoped>
.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 0.9em;
}

.hint {
    color: #7f8c8d;
    font-size: 0.8em;
    display: block;
    margin-top: 4px;
}

.action-group {
    display: flex;
    gap: 5px;
}
</style>

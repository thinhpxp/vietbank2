<template>
    <div class="admin-page">
        <div class="page-header">
            <h2>Quản lý Loại Đối tượng (Object Types)</h2>
            <button class="btn-primary" @click="openCreateModal">+ Thêm Loại mới</button>
        </div>

        <div class="table-container">
            <table class="admin-table">
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
                            <span v-if="type.is_system" class="badge-system">System</span>
                            <span v-else class="badge-custom">Custom</span>
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
        </div>

        <!-- Modal Create/Edit -->
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal-content">
                <h3>{{ isEdit ? 'Cập nhật Loại' : 'Thêm Loại mới' }}</h3>

                <div class="form-group">
                    <label>Mã loại (Code) *</label>
                    <input v-model="formData.code" :disabled="isEdit" placeholder="VD: PROJECT" class="form-control" />
                    <small class="hint">Viết hoa, không dấu, không khoảng trắng.</small>
                </div>

                <div class="form-group">
                    <label>Tên hiển thị *</label>
                    <input v-model="formData.name" placeholder="VD: Dự án" class="form-control" />
                </div>

                <div class="form-group">
                    <label>Trường định danh (key)</label>
                    <input v-model="formData.identity_field_key" placeholder="VD: ho_ten, bien_so_xe"
                        class="form-control" />
                    <small class="hint">Placeholder key của trường dùng để làm tên định danh.</small>
                </div>

                <div class="form-group">
                    <label>Mô tả</label>
                    <textarea v-model="formData.description" class="form-control" rows="3"></textarea>
                </div>

                <div class="modal-actions">
                    <button class="btn-action btn-secondary" @click="closeModal">Hủy</button>
                    <button class="btn-action btn-primary" @click="saveType">Lưu</button>
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
    },
    methods: {
        async fetchTypes() {
            try {
                const res = await axios.get('http://127.0.0.1:8000/api/object-types/');
                this.types = res.data;
            } catch (e) {
                console.error(e);
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
.action-group {
    display: flex;
    gap: 5px;
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
}

.modal-content {
    background: white;
    padding: 25px;
    border-radius: 8px;
    width: 400px;
}

.form-group {
    margin-bottom: 15px;
    text-align: left;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-control {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.hint {
    color: #7f8c8d;
    font-size: 0.85em;
}
</style>

<template>
    <div class="admin-page">
        <h2>Quản lý Cấu hình Form</h2>

        <!-- Form thêm mới -->
        <div class="admin-panel">
            <h4>Thêm Form mới</h4>
            <div class="admin-row mb-2">
                <input v-model="newForm.name" placeholder="Tên Form (VD: Tín dụng tiêu dùng)" class="admin-input">
                <input v-model="newForm.slug" placeholder="Mã định danh (VD: loan-consumer)" class="admin-input">
                <input v-model="newForm.note" placeholder="Ghi chú" class="admin-input">
                <button @click="addForm" class="btn-action btn-create">Thêm</button>
            </div>
        </div>

        <!-- Danh sách -->
        <div class="ui-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tên Form</th>
                        <th>Mã (Slug)</th>
                        <th>Ghi chú</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="f in forms" :key="f.id">
                        <td>{{ f.id }}</td>
                        <td>
                            <input v-if="editingId === f.id" v-model="f.name">
                            <span v-else>{{ f.name }}</span>
                        </td>
                        <td>
                            <input v-if="editingId === f.id" v-model="f.slug">
                            <span v-else>{{ f.slug }}</span>
                        </td>
                        <td>
                            <input v-if="editingId === f.id" v-model="f.note">
                            <span v-else>{{ f.note }}</span>
                        </td>
                        <td>
                            <div class="flex gap-2">
                                <button v-if="editingId === f.id" @click="updateForm(f)"
                                    class="btn-action btn-save">Lưu</button>
                                <button v-else @click="editingId = f.id" class="btn-action btn-edit">Sửa</button>
                                <button @click="deleteForm(f.id)" class="btn-action btn-delete">Xóa</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
            :message="`Bạn có chắc muốn xóa form '${deleteTargetName}'?`" confirmText="Xóa" @confirm="confirmDelete"
            @cancel="showDeleteModal = false" />

        <!-- Generic Modals -->
        <ConfirmModal :visible="showErrorModal" type="error" mode="alert" :title="errorModalTitle"
            :message="errorModalMessage" :errorCode="errorModalCode" :details="errorModalDetails" :showTimestamp="true"
            confirmText="Đóng" @confirm="showErrorModal = false" @cancel="showErrorModal = false" />
        <ConfirmModal :visible="showSuccessModal" type="success" mode="alert" :title="successModalTitle"
            :message="successModalMessage" confirmText="OK" @confirm="showSuccessModal = false"
            @cancel="showSuccessModal = false" />
        <ConfirmModal :visible="showWarningModal" type="warning" mode="alert" :title="warningModalTitle"
            :message="warningModalMessage" confirmText="Đóng" @confirm="showWarningModal = false"
            @cancel="showWarningModal = false" />
    </div>
</template>

<script>
import axios from 'axios';
import { makeTableResizable } from '../../utils/resizable-table';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';

export default {
    components: { ConfirmModal },
    mixins: [errorHandlingMixin],
    data() {
        return {
            forms: [],
            editingId: null,
            newForm: { name: '', slug: '', note: '' },
            showDeleteModal: false,
            deleteTargetId: null,
            deleteTargetName: ''
        }
    },
    mounted() {
        this.fetchData();
        this.initResizable();
    },
    methods: {
        async fetchData() {
            const res = await axios.get('http://127.0.0.1:8000/api/form-views/');
            this.forms = res.data;
            this.$nextTick(() => this.initResizable());
        },
        initResizable() {
            const table = this.$el.querySelector('.data-table');
            if (table) {
                makeTableResizable(table, 'admin-forms');
            }
        },
        async addForm() {
            if (!this.newForm.name || !this.newForm.slug) {
                this.showWarning('Vui lòng nhập đủ Tên và Slug!', 'Thiếu thông tin');
                return;
            }
            try {
                await axios.post('http://127.0.0.1:8000/api/form-views/', this.newForm);
                this.newForm = { name: '', slug: '', note: '' };
                this.fetchData();
                this.showSuccess('Thêm form thành công!');
            } catch (e) {
                this.showError(e, 'Lỗi khi thêm form');
            }
        },
        async updateForm(f) {
            try {
                await axios.put(`http://127.0.0.1:8000/api/form-views/${f.id}/`, f);
                this.editingId = null;
                this.fetchData();
            } catch (e) {
                this.showError(e, 'Lỗi cập nhật form');
            }
        },
        deleteForm(id) {
            const form = this.forms.find(f => f.id === id);
            this.deleteTargetId = id;
            this.deleteTargetName = form ? form.name : '';
            this.showDeleteModal = true;
        },
        async confirmDelete() {
            if (this.deleteTargetId) {
                try {
                    await axios.delete(`http://127.0.0.1:8000/api/form-views/${this.deleteTargetId}/`);
                    this.showDeleteModal = false;
                    this.deleteTargetId = null;
                    this.fetchData();
                    this.showSuccess('Đã xóa form!');
                } catch (e) {
                    this.showError(e, 'Lỗi xóa form');
                }
            }
        }
    }
}
</script>

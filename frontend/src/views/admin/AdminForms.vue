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
        <div class="filter-bar mb-4">
            <div class="filter-group">
                <label>Tìm kiếm:</label>
                <input v-model="filters.search" placeholder="Tìm theo tên hoặc mã..." class="admin-form-control"
                    style="width: 300px">
            </div>
        </div>
        <div class="ui-table-wrapper">
            <vxe-table :data="filteredForms" border show-header-overflow show-overflow resizable
                :column-config="{ resizable: true }" :sort-config="{ trigger: 'cell' }" class="data-table-vxe">
                <vxe-column field="id" title="ID" width="80" sortable></vxe-column>
                <vxe-column field="name" title="Tên Form" min-width="250" sortable>
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="row.name" class="vxe-input-minimal">
                        <span v-else>{{ row.name }}</span>
                    </template>
                </vxe-column>
                <vxe-column field="slug" title="Mã (Slug)" min-width="150" sortable>
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="row.slug" class="vxe-input-minimal">
                        <span v-else>{{ row.slug }}</span>
                    </template>
                </vxe-column>
                <vxe-column field="note" title="Ghi chú" min-width="200">
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="row.note" class="vxe-input-minimal">
                        <span v-else>{{ row.note }}</span>
                    </template>
                </vxe-column>
                <vxe-column title="Hành động" width="150" fixed="right">
                    <template #default="{ row }">
                        <div class="flex gap-2">
                            <button v-if="editingId === row.id" @click="updateForm(row)"
                                class="btn-action btn-save">Lưu</button>
                            <button v-else @click="editingId = row.id" class="btn-action btn-edit">Sửa</button>
                            <button @click="deleteForm(row.id)" class="btn-action btn-delete">Xóa</button>
                        </div>
                    </template>
                </vxe-column>
            </vxe-table>
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
import { API_URL } from '@/store/auth';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
    components: { ConfirmModal },
    mixins: [errorHandlingMixin, FilterableTableMixin],
    data() {
        return {
            forms: [],
            editingId: null,
            filters: { search: '' },
            newForm: { name: '', slug: '', note: '' },
            showDeleteModal: false,
            deleteTargetId: null,
            deleteTargetName: ''
        }
    },
    computed: {
        filteredForms() {
            return this.filterArray(this.forms, this.filters, {
                search: { type: 'text', fields: ['name', 'slug'] }
            });
        }
    },
    mounted() {
        this.fetchData();
    },
    methods: {
        async fetchData() {
            try {
                const res = await axios.get(`${API_URL}/form-views/`);
                this.forms = res.data;
            } catch (e) {
                this.showError(e, 'Lỗi tải danh sách Form');
            }
        },
        async addForm() {
            if (!this.newForm.name || !this.newForm.slug) {
                this.showWarning('Vui lòng nhập đủ Tên và Slug!', 'Thiếu thông tin');
                return;
            }
            try {
                await axios.post(`${API_URL}/form-views/`, this.newForm);
                this.newForm = { name: '', slug: '', note: '' };
                this.fetchData();
                this.showSuccess('Thêm form thành công!');
            } catch (e) {
                this.showError(e, 'Lỗi khi thêm form');
            }
        },
        async updateForm(f) {
            try {
                await axios.put(`${API_URL}/form-views/${f.id}/`, f);
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
                    await axios.delete(`${API_URL}/form-views/${this.deleteTargetId}/`);
                    this.showDeleteModal = false;
                    this.deleteTargetId = null;
                    this.fetchData();
                    this.showSuccess('Đã xóa form!');
                } catch (e) {
                    this.showDeleteModal = false;
                    this.showError(e, 'Lỗi xóa form');
                }
            }
        }
    }
}
</script>

<style scoped>
.data-table-vxe {
    margin-top: 10px;
}
</style>

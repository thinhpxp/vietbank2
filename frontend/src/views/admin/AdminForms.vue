<template>
    <div class="admin-page">
        <h2>Quản lý Cấu hình Form</h2>

        <!-- Form thêm mới -->
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
</template>

<script>
import axios from 'axios';
import { makeTableResizable } from '../../utils/resizable-table';

export default {
    data() {
        return {
            forms: [],
            editingId: null,
            newForm: { name: '', slug: '', note: '' }
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
            if (!this.newForm.name || !this.newForm.slug) return alert('Vui lòng nhập đủ Tên và Slug!');
            try {
                await axios.post('http://127.0.0.1:8000/api/form-views/', this.newForm);
                this.newForm = { name: '', slug: '', note: '' };
                this.fetchData();
            } catch (e) { alert('Lỗi: ' + JSON.stringify(e.response.data)); }
        },
        async updateForm(f) {
            try {
                await axios.put(`http://127.0.0.1:8000/api/form-views/${f.id}/`, f);
                this.editingId = null;
                this.fetchData();
            } catch (e) { alert('Lỗi: ' + JSON.stringify(e.response.data)); }
        },
        async deleteForm(id) {
            if (!confirm('Bạn có chắc muốn xóa?')) return;
            await axios.delete(`http://127.0.0.1:8000/api/form-views/${id}/`);
            this.fetchData();
        }
    }
}
</script>

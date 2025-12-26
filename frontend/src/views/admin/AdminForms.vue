<template>
    <div>
        <h2>Quản lý Cấu hình Form</h2>

        <!-- Form thêm mới -->
        <div class="add-box">
            <h4>Thêm Form mới</h4>
            <div class="row">
                <input v-model="newForm.name" placeholder="Tên Form (VD: Tín dụng tiêu dùng)">
                <input v-model="newForm.slug" placeholder="Mã định danh (VD: loan-consumer)">
                <input v-model="newForm.note" placeholder="Ghi chú">
                <button @click="addForm" class="btn-create">Thêm</button>
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
                        <button v-if="editingId === f.id" @click="updateForm(f)" class="btn-create">Lưu</button>
                        <button v-else @click="editingId = f.id">Sửa</button>
                        <button @click="deleteForm(f.id)" class="btn-delete">Xóa</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            forms: [],
            editingId: null,
            newForm: { name: '', slug: '', note: '' }
        }
    },
    mounted() { this.fetchData(); },
    methods: {
        async fetchData() {
            const res = await axios.get('http://127.0.0.1:8000/api/form-views/');
            this.forms = res.data;
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

<style scoped>
.add-box {
    background: #eee;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 5px;
}

.row {
    display: flex;
    gap: 10px;
}

.row input {
    padding: 8px;
    flex: 1;
}

.btn-create {
    background: #42b983;
    color: white;
    border: none;
    padding: 8px 15px;
    cursor: pointer;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

.data-table th,
.data-table td {
    padding: 10px;
    border: 1px solid #ddd;
    text-align: left;
}

.btn-delete {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    margin-left: 5px;
}
</style>

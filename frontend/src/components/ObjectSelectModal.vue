<template>
    <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content master-select-modal">
            <div class="modal-header">
                <h3>{{ title }}</h3>
                <button class="btn-close" @click="$emit('close')">&times;</button>
            </div>

            <div class="modal-body">
                <div class="search-box">
                    <input v-model="searchQuery" :placeholder="searchPlaceholder" class="search-input"
                        @keyup.enter="handleSearch">
                    <button class="btn-search" @click="handleSearch">Tìm kiếm</button>
                </div>

                <div v-if="loading" class="loading">Đang tải dữ liệu...</div>

                <div v-else class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr v-if="type === 'person'">
                                <th>Họ tên</th>
                                <th>CCCD</th>
                                <th>Cập nhật gần nhất</th>
                                <th>Thao tác</th>
                            </tr>
                            <tr v-else>
                                <th>Số Giấy chứng nhận</th>
                                <th>Người sở hữu</th>
                                <th>Cập nhật gần nhất</th>
                                <th>Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in filteredItems" :key="item.id">
                                <template v-if="type === 'person'">
                                    <td>{{ item.ho_ten || 'N/A' }}</td>
                                    <td>{{ item.cccd_so || 'N/A' }}</td>
                                </template>
                                <template v-else>
                                    <td>{{ item.so_giay_chung_nhan || 'N/A' }}</td>
                                    <td>{{ item.owner_name || 'N/A' }}</td>
                                </template>
                                <td>
                                    <div class="update-info">
                                        <span>{{ formatDate(item.updated_at) }}</span>
                                        <small class="text-muted" v-if="item.last_updated_by_name">by {{
                                            item.last_updated_by_name }}</small>
                                    </div>
                                </td>
                                <td>
                                    <button class="btn-select" @click="selectItem(item)">Chọn</button>
                                </td>
                            </tr>
                            <tr v-if="filteredItems.length === 0">
                                <td colspan="4" class="text-center">Không tìm thấy kết quả phù hợp.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ObjectSelectModal',
    props: {
        isOpen: Boolean,
        type: {
            type: String,
            default: 'person' // 'person' or 'asset'
        }
    },
    data() {
        return {
            items: [],
            searchQuery: '',
            loading: false
        };
    },
    computed: {
        title() {
            return this.type === 'person' ? 'Chọn Người từ danh sách' : 'Chọn Tài sản từ danh sách';
        },
        searchPlaceholder() {
            return this.type === 'person' ? 'Tìm theo Tên hoặc CCCD...' : 'Tìm theo Số Giấy chứng nhận...';
        },
        filteredItems() {
            if (!this.searchQuery) return this.items;
            const query = this.searchQuery.toLowerCase();
            return this.items.filter(item => {
                if (this.type === 'person') {
                    return (item.ho_ten && item.ho_ten.toLowerCase().includes(query)) ||
                        (item.cccd_so && item.cccd_so.includes(query));
                } else {
                    return item.so_giay_chung_nhan && item.so_giay_chung_nhan.toLowerCase().includes(query);
                }
            });
        }
    },
    watch: {
        isOpen(val) {
            if (val) {
                this.fetchItems();
            }
        }
    },
    methods: {
        async fetchItems() {
            this.loading = true;
            try {
                const endpoint = this.type === 'person' ? 'master-people' : 'master-assets';
                const response = await axios.get(`http://127.0.0.1:8000/api/${endpoint}/`);
                this.items = response.data;
            } catch (error) {
                console.error('Lỗi khi tải dữ liệu master:', error);
            } finally {
                this.loading = false;
            }
        },
        selectItem(item) {
            this.$emit('select', item);
            this.$emit('close');
        },
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleString('vi-VN');
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
    justify-content: center;
    align-items: center;
    z-index: 2000;
}

.modal-content.master-select-modal {
    background: white;
    width: 70%;
    max-width: 900px;
    max-height: 80vh;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
}

.modal-header {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-body {
    padding: 20px;
    overflow-y: auto;
}

.search-box {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.search-input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.btn-search {
    background: #3498db;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    cursor: pointer;
}

.table-container {
    border: 1px solid #eee;
    border-radius: 4px;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th {
    background: #f8f9fa;
    text-align: left;
    padding: 10px;
    border-bottom: 2px solid #eee;
}

.data-table td {
    padding: 10px;
    border-bottom: 1px solid #eee;
}

.update-info {
    display: flex;
    flex-direction: column;
}

.btn-select {
    background: #27ae60;
    color: white;
    border: none;
    padding: 5px 12px;
    border-radius: 4px;
    cursor: pointer;
}

.btn-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
}

.text-center {
    text-align: center;
}

.text-muted {
    color: #888;
    font-size: 0.8em;
}
</style>

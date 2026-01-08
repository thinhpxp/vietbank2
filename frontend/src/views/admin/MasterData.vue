<template>
    <div class="admin-page dashboard-container">
        <div class="header-actions">
            <h2>Quản lý Dữ liệu gốc (Master Data)</h2>
            <div class="action-buttons" style="display: flex; gap: 10px;">
                <button class="btn-action btn-secondary" @click="fetchData" :disabled="loading">
                    <span v-if="loading">⏳...</span>
                    <span v-else>🔄 Làm mới</span>
                </button>
                <button class="btn-action btn-create" @click="openCreateModal">+ Thêm mới</button>
            </div>
        </div>

        <!-- TABS -->
        <div class="tabs-header">
            <button v-for="type in objectTypes" :key="type.code" class="tab-item"
                :class="{ active: activeTab === type.code }" @click="activeTab = type.code">
                {{ type.name }}
            </button>
        </div>

        <div class="tab-content">
            <div v-if="loading" class="loading-state">Đang tải dữ liệu...</div>
            <table v-else class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <!-- Dynamic Headers based on Type could be improved later, for now Generic -->
                        <th>Tên / Số hiệu</th>
                        <th>Thông tin thêm</th>
                        <th>Ngày tạo</th>
                        <th>Cập nhật gần nhất</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in items" :key="item.id">
                        <td>
                            {{ item.id }}
                            <div v-if="item.profiles_count === 0" class="badge-unlinked">Chưa liên kết</div>
                        </td>
                        <td class="font-bold">
                            <!-- Hiển thị tên hoặc số GCN tùy loại, hoặc fallback display_name -->
                            {{ item.ho_ten || item.so_giay_chung_nhan || item.display_name || '---' }}
                        </td>
                        <td>
                            <!-- Hiển thị CCCD hoặc Chủ sở hữu -->
                            <span v-if="activeTab === 'PERSON'">CCCD: {{ item.cccd }}</span>
                            <span v-else-if="activeTab === 'VEHICLE'">Hãng: {{ item.nhan_hieu_xe }}</span>
                            <span v-else-if="activeTab === 'REALESTATE'">Số vào sổ: {{ item.so_vao_so }}</span>
                            <span v-else>{{ item.owner_name }}</span>
                        </td>
                        <td>{{ formatDate(item.created_at) }}</td>
                        <td>
                            <div class="audit-info">
                                <div>{{ formatDate(item.updated_at) }}</div>
                                <small class="user-badge" v-if="item.last_updated_by_name">
                                    👤 {{ item.last_updated_by_name }}
                                </small>
                            </div>
                        </td>
                        <td>
                            <div class="action-group">
                                <button class="btn-action btn-secondary" @click="viewRelated(item, 'profiles')">Hồ
                                    sơ</button>
                                <button class="btn-action btn-edit" @click="editObject(item)">Sửa</button>
                                <button class="btn-action btn-delete" @click="confirmDelete(item)">Xóa</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- RELATED INFO MODAL -->
        <div v-if="showRelatedModal" class="modal-overlay" @click.self="showRelatedModal = false">
            <div class="modal-content side-modal">
                <div class="modal-header">
                    <h3>{{ relatedTitle }}</h3>
                    <button class="btn-close" @click="showRelatedModal = false">&times;</button>
                </div>
                <div class="modal-body">
                    <div v-if="relatedLoading">Đang tải...</div>
                    <ul class="related-list" v-else-if="relatedData.length > 0">
                        <li v-for="item in relatedData" :key="item.id" class="related-item">
                            <div v-if="relatedType.includes('profiles')">
                                <div class="item-title">📄 {{ item.name }}</div>
                                <div class="item-sub">
                                    <span>Loại: {{ item.form_name }}</span> |
                                    <span>Ngày: {{ formatDate(item.created_at) }}</span>
                                </div>
                                <button class="btn-link" @click="goToProfile(item.id)">Mở Hồ sơ</button>
                            </div>
                            <div v-else-if="relatedType === 'assets'">
                                <div class="item-title">🏠 Số GCN: {{ item.so_giay_chung_nhan }}</div>
                                <div class="item-sub">Ngày nhập: {{ formatDate(item.created_at) }}</div>
                            </div>
                        </li>
                    </ul>
                    <div v-else class="empty-state">Không có dữ liệu liên quan.</div>
                </div>
            </div>
        </div>

        <!-- Confirm Delete Modal -->
        <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
            :message="`Bạn có chắc muốn xóa đối tượng này? Thao tác này sẽ gỡ liên kết khỏi các hồ sơ cũ nhưng không xóa dữ liệu trong hồ sơ.`"
            confirmText="Xóa" @confirm="executeDelete" @cancel="showDeleteModal = false" />

        <!-- CREATE/EDIT MODAL -->
        <MasterCreateModal :isOpen="showCreateModal" :type="activeTab" :typeName="currentTypeName"
            :editObject="targetEditObject" @close="showCreateModal = false" @success="fetchData" />
    </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';
import MasterCreateModal from '../../components/MasterCreateModal.vue';
import { makeTableResizable } from '../../utils/resizable-table';

export default {
    name: 'MasterData',
    components: { ConfirmModal, MasterCreateModal },
    data() {
        return {
            objectTypes: [], // List of dynamic types
            activeTab: '', // Code of active type
            loading: false,
            items: [], // Unified list for the current tab

            // Related Modal
            showRelatedModal: false,
            relatedType: '',
            relatedTitle: '',
            relatedData: [],
            relatedLoading: false,

            // Delete
            showDeleteModal: false,
            deleteTarget: null,
            // deleteTargetType: '', // Không cần nữa, dùng activeTab code

            // Create/Edit
            showCreateModal: false,
            targetEditObject: null
        };
    },
    computed: {
        // currentEntityType() { ... } // Không cần nữa vì activeTab chính là code (PERSON, ASSET...)
        currentTypeName() {
            const t = this.objectTypes.find(type => type.code === this.activeTab);
            return t ? t.name : 'Đối tượng';
        }
    },
    watch: {
        activeTab: {
            handler(newVal) {
                if (newVal) this.fetchData();
            }
        }
    },
    async mounted() {
        await this.fetchObjectTypes();
        this.initResizable();
    },
    methods: {
        async fetchObjectTypes() {
            try {
                const res = await axios.get('http://127.0.0.1:8000/api/object-types/');
                this.objectTypes = res.data;
                if (this.objectTypes.length > 0) {
                    this.activeTab = this.objectTypes[0].code;
                }
            } catch (e) {
                console.error("Lỗi tải loại đối tượng:", e);
            }
        },
        async fetchData() {
            if (!this.activeTab) return;
            this.loading = true;
            try {
                const response = await axios.get(`http://127.0.0.1:8000/api/master-objects/?object_type=${this.activeTab}`);

                // Flatten
                this.items = response.data.map(item => ({
                    ...item,
                    ...item.field_values
                }));

            } catch (error) {
                console.error('Lỗi khi tải dữ liệu master:', error);
            } finally {
                this.loading = false;
                this.$nextTick(() => {
                    this.initResizable();
                });
            }
        },
        initResizable() {
            const table = this.$el.querySelector('.data-table');
            if (table) {
                makeTableResizable(table, 'master-data-' + this.activeTab);
            }
        },
        async viewRelated(obj, type) {
            this.relatedType = type;
            this.showRelatedModal = true;
            this.relatedLoading = true;


            let action = '';

            if (type === 'profiles') {
                this.relatedTitle = `Hồ sơ liên quan: ${obj.ho_ten || obj.display_name}`;
                action = 'related_profiles';
            } else if (type === 'assets') {
                this.relatedTitle = `Tài sản sở hữu: ${obj.ho_ten || obj.display_name}`;
                // Link logic for generic not implemented yet, fallback to profiles or specific API
                action = 'related_profiles'; // Placeholder
            } else if (type === 'asset_profiles') {
                this.relatedTitle = `Hồ sơ chứa tài sản: ${obj.so_giay_chung_nhan || obj.display_name}`;
                action = 'related_profiles';
            }

            try {
                const response = await axios.get(`http://127.0.0.1:8000/api/master-objects/${obj.id}/${action}/`);
                this.relatedData = response.data;
            } catch (error) {
                console.error('Lỗi khi tải dữ liệu liên quan:', error);
            } finally {
                this.relatedLoading = false;
            }
        },
        formatDate(dateString) {
            if (!dateString) return '---';
            return new Date(dateString).toLocaleDateString('vi-VN', {
                year: 'numeric', month: '2-digit', day: '2-digit',
                hour: '2-digit', minute: '2-digit'
            });
        },
        confirmDelete(obj, type) {
            this.deleteTarget = obj;
            this.deleteTargetType = type;
            this.showDeleteModal = true;
        },
        async executeDelete() {
            try {
                await axios.delete(`http://127.0.0.1:8000/api/master-objects/${this.deleteTarget.id}/`);
                this.showDeleteModal = false;
                this.fetchData();
                alert('Đã xóa thành công!');
            } catch (error) {
                alert('Lỗi khi xóa: ' + error.message);
            }
        },
        openCreateModal() {
            this.targetEditObject = null;
            this.showCreateModal = true;
        },
        editObject(obj) {
            this.targetEditObject = obj;
            this.showCreateModal = true;
        },
        goToProfile(id) {
            this.$router.push(`/profile/${id}`);
        }
    }
};
</script>

<style scoped>
.badge-unlinked {
    background: #fff3e0;
    color: #e67e22;
    font-size: 0.75em;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid #ffe0b2;
    display: inline-block;
    margin-top: 4px;
    font-weight: bold;
}

.tabs-header {
    display: flex;
    gap: 5px;
    margin-bottom: 20px;
    border-bottom: 2px solid #eee;
}

.tab-item {
    padding: 12px 25px;
    background: #f8f9fa;
    border: 1px solid #eee;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    color: #666;
    transition: all 0.3s;
}

.tab-item.active {
    background: #3498db;
    color: white;
    border-color: #3498db;
}

.audit-info {
    font-size: 0.9em;
}

.user-badge {
    background: #e9ecef;
    padding: 2px 6px;
    border-radius: 4px;
    color: #495057;
    display: inline-block;
    margin-top: 4px;
}

.action-group {
    display: flex;
    gap: 5px;
}

/* Modal styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: flex-end;
    /* Slide in from right effect */
    z-index: 2000;
}

.modal-content.side-modal {
    background: white;
    width: 400px;
    height: 100%;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
}

.modal-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-body {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
}

.related-list {
    list-style: none;
    padding: 0;
}

.related-item {
    padding: 15px;
    border: 1px solid #eee;
    border-radius: 8px;
    margin-bottom: 10px;
    background: #fcfcfc;
}

.item-title {
    font-weight: bold;
    margin-bottom: 5px;
}

.item-sub {
    font-size: 0.85em;
    color: #666;
    margin-bottom: 10px;
}

.btn-link {
    background: #f8f9fa;
    border: 1px solid #ddd;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85em;
}

.btn-link:hover {
    background: #e9ecef;
}
</style>

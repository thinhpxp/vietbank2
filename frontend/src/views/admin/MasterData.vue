<template>
    <div class="dashboard-container">
        <div class="header-actions">
            <h2>Quản lý Dữ liệu gốc (Master Data)</h2>
            <button class="btn-create-master" @click="openCreateModal">+ Thêm mới</button>
        </div>

        <!-- TABS -->
        <div class="tabs-header">
            <button class="tab-item" :class="{ active: activeTab === 'people' }" @click="activeTab = 'people'">
                👥 Danh sách Người liên quan
            </button>
            <button class="tab-item" :class="{ active: activeTab === 'assets' }" @click="activeTab = 'assets'">
                🏠 Danh mục Tài sản
            </button>
            <button class="tab-item" :class="{ active: activeTab === 'savings' }" @click="activeTab = 'savings'">
                📒 Sổ tiết kiệm (Mới)
            </button>
        </div>

        <div class="tab-content">
            <!-- TAB: PEOPLE -->
            <div v-if="activeTab === 'people'">
                <div v-if="loading" class="loading-state">Đang tải dữ liệu người...</div>
                <table v-else class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Họ tên</th>
                            <th>CCCD</th>
                            <th>Ngày tạo</th>
                            <th>Cập nhật gần nhất</th>
                            <th>Hành động</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="person in people" :key="person.id">
                            <td>
                                {{ person.id }}
                                <div v-if="person.profiles_count === 0" class="badge-unlinked">Chưa liên kết</div>
                            </td>
                            <td class="font-bold">{{ person.ho_ten || '---' }}</td>
                            <td>{{ person.cccd_so || '---' }}</td>
                            <td>{{ formatDate(person.created_at) }}</td>
                            <td>
                                <div class="audit-info">
                                    <div>{{ formatDate(person.updated_at) }}</div>
                                    <small class="user-badge" v-if="person.last_updated_by_name">
                                        👤 {{ person.last_updated_by_name }}
                                    </small>
                                </div>
                            </td>
                            <td>
                                <div class="action-group">
                                    <button class="btn-info" @click="viewRelated(person, 'profiles')">Hồ sơ</button>
                                    <button class="btn-info" @click="viewRelated(person, 'assets')">Tài sản</button>
                                    <button class="btn-edit" @click="editObject(person, 'person')">Sửa</button>
                                    <button class="btn-delete" @click="confirmDelete(person, 'person')">Xóa</button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- TAB: ASSETS -->
            <div v-if="activeTab === 'assets'">
                <div v-if="loading" class="loading-state">Đang tải dữ liệu tài sản...</div>
                <table v-else class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Số Giấy chứng nhận</th>
                            <th>Người sở hữu</th>
                            <th>Ngày tạo</th>
                            <th>Cập nhật gần nhất</th>
                            <th>Hành động</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="asset in assets" :key="asset.id">
                            <td>
                                {{ asset.id }}
                                <div v-if="asset.profiles_count === 0" class="badge-unlinked">Chưa liên kết</div>
                            </td>
                            <td class="font-bold">{{ asset.so_giay_chung_nhan || '---' }}</td>
                            <td>{{ asset.owner_name || '---' }}</td>
                            <td>{{ formatDate(asset.created_at) }}</td>
                            <td>
                                <div class="audit-info">
                                    <div>{{ formatDate(asset.updated_at) }}</div>
                                    <small class="user-badge" v-if="asset.last_updated_by_name">
                                        👤 {{ asset.last_updated_by_name }}
                                    </small>
                                </div>
                            </td>
                            <td>
                                <div class="action-group">
                                    <button class="btn-info" @click="viewRelated(asset, 'asset_profiles')">Hồ
                                        sơ</button>
                                    <button class="btn-edit" @click="editObject(asset, 'asset')">Sửa</button>
                                    <button class="btn-delete" @click="confirmDelete(asset, 'asset')">Xóa</button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
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
        <MasterCreateModal :isOpen="showCreateModal" :type="currentEntityType" :editObject="targetEditObject"
            @close="showCreateModal = false" @success="fetchData" />
    </div>
</template>

<script>
import axios from 'axios';
import ConfirmModal from '../../components/ConfirmModal.vue';
import MasterCreateModal from '../../components/MasterCreateModal.vue';

export default {
    name: 'MasterData',
    components: { ConfirmModal, MasterCreateModal },
    data() {
        return {
            activeTab: 'people',
            loading: false,
            people: [],
            assets: [],

            // Related Modal
            showRelatedModal: false,
            relatedType: '',
            relatedTitle: '',
            relatedData: [],
            relatedLoading: false,

            // Delete
            showDeleteModal: false,
            deleteTarget: null,
            deleteTargetType: '',

            // Create/Edit
            showCreateModal: false,
            targetEditObject: null
        };
    },
    computed: {
        currentEntityType() {
            return {
                'people': 'PERSON',
                'assets': 'ASSET',
                'savings': 'SAVINGS'
            }[this.activeTab];
        }
    },
    watch: {
        activeTab: {
            immediate: true,
            handler() {
                this.fetchData();
            }
        }
    },
    methods: {
        async fetchData() {
            this.loading = true;
            try {
                // Sổ tiết kiệm tạm thời chưa có Backend, dùng chung một endpoint mẫu hoặc handle trống
                if (this.activeTab === 'savings') {
                    this.assets = []; // Hoặc nạp từ master-savings nếu có
                    return;
                }

                const endpoint = this.activeTab === 'people' ? 'master-people' : 'master-assets';
                const response = await axios.get(`http://127.0.0.1:8000/api/${endpoint}/`);
                if (this.activeTab === 'people') {
                    this.people = response.data;
                } else {
                    this.assets = response.data;
                }
            } catch (error) {
                console.error('Lỗi khi tải dữ liệu master:', error);
            } finally {
                this.loading = false;
            }
        },
        async viewRelated(obj, type) {
            this.relatedType = type;
            this.showRelatedModal = true;
            this.relatedLoading = true;

            let masterType = '';
            let action = '';

            if (type === 'profiles') {
                this.relatedTitle = `Hồ sơ liên quan: ${obj.ho_ten}`;
                masterType = 'master-people';
                action = 'related_profiles';
            } else if (type === 'assets') {
                this.relatedTitle = `Tài sản sở hữu: ${obj.ho_ten}`;
                masterType = 'master-people';
                action = 'related_assets';
            } else if (type === 'asset_profiles') {
                this.relatedTitle = `Hồ sơ chứa tài sản: ${obj.so_giay_chung_nhan}`;
                masterType = 'master-assets';
                action = 'related_profiles';
            }

            try {
                const response = await axios.get(`http://127.0.0.1:8000/api/${masterType}/${obj.id}/${action}/`);
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
                const endpoint = this.deleteTargetType === 'person' ? 'master-people' : 'master-assets';
                await axios.delete(`http://127.0.0.1:8000/api/${endpoint}/${this.deleteTarget.id}/`);
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
/* Reuse styles from DashboardView.vue */
.dashboard-container {
    max-width: 95%;
    margin: 20px auto;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.btn-create-master {
    background: #27ae60;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s;
}

.btn-create-master:hover {
    background: #219150;
}

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

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th {
    background: #f1f3f5;
    padding: 12px;
    text-align: left;
    font-size: 14px;
}

.data-table td {
    padding: 12px;
    border-bottom: 1px solid #eee;
}

.font-bold {
    font-weight: bold;
    color: #2c3e50;
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

.btn-info {
    background: #17a2b8;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
}

.btn-edit {
    background: #3498db;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
}

.btn-delete {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
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

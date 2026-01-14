<template>
    <div class="admin-page dashboard-container">
        <div class="header-actions">
            <h2>Quản lý Dữ liệu gốc (Master Data)</h2>
            <div class="action-buttons" style="display: flex; gap: 10px;">
                <button class="btn-action btn-secondary" @click="fetchData" :disabled="loading">
                    <span v-if="loading">⏳...</span>
                    <span v-else>🔄 Làm mới</span>
                </button>
                <button class="btn-action btn-create" @click="openCreateModal()">+ Thêm mới</button>
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
                            <span v-else-if="activeTab === 'BOND'">Kỳ hạn: {{ item.ky_han_trai_phieu }}</span>
                            <span v-else-if="activeTab === 'SAVINGS'">Số tiền: {{ item.so_tien_goi }}</span>
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
                                <button class="btn-action btn-secondary" @click="viewRelated(item)">Liên kết</button>
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
            <div class="modal-content side-modal" :style="{ width: sideModalWidth + 'px' }">
                <!-- RESIZE HANDLE -->
                <div class="resizer-handle" @mousedown="startResize"></div>

                <div class="modal-header">
                    <h3>{{ relatedTitle }}</h3>
                    <button class="btn-close" @click="showRelatedModal = false">&times;</button>
                </div>
                <div class="modal-body">
                    <div v-if="relatedLoading">Đang tải...</div>
                    <div v-else>
                        <!-- TABS IN MODAL -->
                        <div class="modal-tabs">
                            <button :class="{ active: relatedTab === 'profiles' }" @click="relatedTab = 'profiles'">Hồ
                                sơ
                                ({{ relatedProfiles.length }})</button>
                            <button v-if="relatedType === 'PERSON'" :class="{ active: relatedTab === 'assets' }"
                                @click="relatedTab = 'assets'">Tài sản ({{ relatedAssets.length }})</button>
                            <button v-if="relatedType !== 'PERSON'" :class="{ active: relatedTab === 'owners' }"
                                @click="relatedTab = 'owners'">Chủ sở hữu ({{ owners.length }})</button>
                        </div>

                        <!-- CONTENT: PROFILES -->
                        <ul v-if="relatedTab === 'profiles'" class="related-list">
                            <li v-for="item in relatedProfiles" :key="item.id" class="related-item">
                                <div class="item-title">📄 {{ item.name }}</div>
                                <div class="item-sub">
                                    <span>Loại: {{ item.form_name }}</span> |
                                    <span>Ngày: {{ formatDate(item.created_at) }}</span>
                                </div>
                                <button class="btn-link" @click="goToProfile(item.id)">Mở Hồ sơ</button>
                            </li>
                            <li v-if="relatedProfiles.length === 0" class="empty-text">Chưa có hồ sơ liên quan.</li>
                        </ul>

                        <!-- CONTENT: ASSETS (For Person) -->
                        <ul v-if="relatedTab === 'assets'" class="related-list">
                            <li v-for="rel in relatedAssets" :key="rel.id" class="related-item">
                                <div class="item-title">🏠 {{ rel.target_name }}</div>
                                <div class="item-sub">
                                    <span>Loại: {{ rel.target_type }}</span> |
                                    <span>Quan hệ: {{ rel.relation_type }}</span>
                                </div>
                                <button class="btn-link" @click="viewChildDetails(rel.target_object)">Xem chi
                                    tiết</button>
                            </li>
                            <li v-if="relatedAssets.length === 0" class="empty-text">Chưa sở hữu tài sản nào.</li>
                        </ul>

                        <!-- CONTENT: OWNERS (For Assets) -->
                        <ul v-if="relatedTab === 'owners'" class="related-list">
                            <li v-for="rel in owners" :key="rel.id" class="related-item">
                                <div class="item-title">👤 {{ rel.source_name }}</div>
                                <div class="item-sub">
                                    <span>Quan hệ: {{ rel.relation_type }}</span>
                                </div>
                                <button class="btn-link" @click="viewChildDetails(rel.source_object)">Xem chi
                                    tiết</button>
                            </li>
                            <li v-if="owners.length === 0" class="empty-text">Chưa xác định chủ sở hữu.</li>
                        </ul>

                    </div>
                </div>
            </div>
        </div>

        <!-- Confirm Delete Modal -->
        <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
            :message="`Bạn có chắc muốn xóa đối tượng này? Thao tác này sẽ gỡ liên kết khỏi các hồ sơ cũ nhưng không xóa dữ liệu trong hồ sơ.`"
            confirmText="Xóa" @confirm="executeDelete" @cancel="showDeleteModal = false" />

        <!-- CREATE/EDIT MODAL -->
        <MasterCreateModal :isOpen="showCreateModal" :type="tempOverrideType || activeTab"
            :typeName="tempOverrideTypeName || currentTypeName" :editObject="targetEditObject"
            @close="showCreateModal = false" @success="fetchData" />
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
            relatedType: '', // PERSON or other
            relatedTitle: '',
            relatedTab: 'profiles', // profiles, assets, owners
            // Data buckets
            relatedProfiles: [],
            relatedAssets: [],
            owners: [],

            relatedLoading: false,

            // Delete
            showDeleteModal: false,
            deleteTarget: null,
            // deleteTargetType: '', // Không cần nữa, dùng activeTab code

            // Create/Edit
            showCreateModal: false,
            targetEditObject: null,

            // Resizing (cleaned up)
            sideModalWidth: 400,
            isResizing: false,

            // Modal Type Override (for viewing cross-type relations)
            tempOverrideType: null,
            tempOverrideTypeName: null
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
        async viewRelated(obj) {
            this.showRelatedModal = true;
            this.relatedLoading = true;
            this.relatedType = obj.object_type; // PERSON, ASSET, etc.
            this.relatedTitle = `Thông tin liên quan: ${obj.ho_ten || obj.display_name}`;
            this.relatedTab = 'profiles'; // Reset tab

            try {
                // 1. Fetch Profile Links (Legacy)
                const resProfiles = await axios.get(`http://127.0.0.1:8000/api/master-objects/${obj.id}/related_profiles/`);
                this.relatedProfiles = resProfiles.data;

                // 2. Fetch Direct Relations (New)
                // We re-fetch the object to get updated 'related_assets' and 'owners' injected by serializer
                const resDetail = await axios.get(`http://127.0.0.1:8000/api/master-objects/${obj.id}/`);
                const detail = resDetail.data;
                this.relatedAssets = detail.related_assets || [];
                this.owners = detail.owners || [];

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
        openCreateModal(objToEdit = null) {
            // Reset overrides explicitly
            this.tempOverrideType = null;
            this.tempOverrideTypeName = null;

            if (objToEdit) {
                // Open details in generic edit mode
                this.targetEditObject = objToEdit;
            } else {
                this.targetEditObject = null;
            }
            this.showCreateModal = true;
        },
        editObject(obj) {
            this.tempOverrideType = null;
            this.tempOverrideTypeName = null;
            this.targetEditObject = obj;
            this.showCreateModal = true;
        },
        goToProfile(id) {
            // Open in new tab as requested
            const routeData = this.$router.resolve({ path: `/edit/${id}` });
            window.open(routeData.href, '_blank');
        },
        async viewChildDetails(objectId) {
            // Fetch full details of the child object then open modal
            try {
                this.relatedLoading = true;
                const res = await axios.get(`http://127.0.0.1:8000/api/master-objects/${objectId}/`);
                // Flatten fields like we do in fetchData
                const fullObj = {
                    ...res.data,
                    ...res.data.field_values
                };

                // Determine type title for the modal
                // We need to guess type name or pass it. 
                // The MasterCreateModal takes 'typeName'. 
                // We can find it in objectTypes if we know the code.
                const typeCode = fullObj.object_type;
                const typeDef = this.objectTypes.find(t => t.code === typeCode);
                const typeName = typeDef ? typeDef.name : typeCode;

                // Use a temporary workaround to open modal with this object type
                // We need to set activeTab temporarily or pass separate props to Modal?
                // MasterCreateModal uses 'type' prop.

                // Let's reuse specific properties for this case
                this.targetEditObject = fullObj;
                // Hack: We might need to handle the 'type' prop of modal if it differs from activeTab
                // But MasterCreateModal only uses 'type' for fetching fields title.
                // We should probably update showCreateModal to handle specific type overriding activeTab
                // But for now let's assume we can pass it via a separate mechanism or just change activeTab?
                // Changing activeTab changes the background list... maybe confusing.

                // Better: Update MasterCreateModal usage in template to accept dynamic type
                // But for now, let's try just setting targetEditObject and hope 
                // Wait, MasterCreateModal props: :type="activeTab".
                // If I am viewing a Person (activeTab=PERSON), and viewing related Asset (VEHICLE),
                // the modal will receive type="PERSON" which is WRONG for VEHICLE fields.

                // FIX: We need a dynamic override.
                this.tempOverrideType = typeCode;
                this.tempOverrideTypeName = typeName;

                this.showCreateModal = true;

            } catch (e) {
                console.error(e);
                this.$toast.error("Không thể tải thông tin chi tiết");
            } finally {
                this.relatedLoading = false;
            }
        },
        // RESIZING LOGIC
        startResize() {
            this.isResizing = true;
            document.body.style.userSelect = 'none'; // Prevent text selection
            document.body.style.cursor = 'col-resize'; // Force cursor
            document.addEventListener('mousemove', this.doResize);
            document.addEventListener('mouseup', this.stopResize);
        },
        doResize(e) {
            if (this.isResizing) {
                // Calculate new width: window width - mouse X
                // Since it is right-aligned
                const newWidth = window.innerWidth - e.clientX;
                if (newWidth > 300 && newWidth < window.innerWidth - 50) {
                    this.sideModalWidth = newWidth;
                }
            }
        },
        stopResize() {
            this.isResizing = false;
            document.body.style.userSelect = '';
            document.body.style.cursor = '';
            document.removeEventListener('mousemove', this.doResize);
            document.removeEventListener('mouseup', this.stopResize);
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
    inset: 0;
    min-width: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 2000;
}

.modal-content.side-modal {
    position: absolute;
    top: 0;
    right: 0;
    height: 100%;
    background: white;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
}

.resizer-handle {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 8px;
    cursor: col-resize;
    z-index: 10;
}

.resizer-handle:hover {
    background: rgba(25, 118, 210, 0.1);
    /* UX improvement */
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

.modal-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

.modal-tabs button {
    background: none;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    font-weight: 600;
    color: #888;
    border-radius: 4px;
}

.modal-tabs button.active {
    background: #e3f2fd;
    color: #1976d2;
}

.empty-text {
    text-align: center;
    color: #999;
    padding: 20px;
}
</style>

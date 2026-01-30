<template>
    <div class="admin-page page-container">
        <div class="page-header">
            <h2>Quản lý Dữ liệu gốc (Master Data)</h2>
            <div class="flex gap-2">
                <button v-if="auth.isSuperuser && selectedIds.length > 0" class="btn-action btn-danger"
                    @click="confirmBulkDelete">
                    <SvgIcon name="trash" size="sm" /> Xóa hàng loạt ({{ selectedIds.length }})
                </button>
                <button class="btn-action btn-secondary" @click="fetchData" :disabled="loading">
                    <span v-if="loading">⏳...</span>
                    <span v-else>🔄 Làm mới</span>
                </button>
                <button class="btn-action btn-create" @click="openCreateModal()">+ Thêm mới</button>
            </div>
        </div>

        <!-- TABS -->
        <div class="admin-tabs">
            <button v-for="type in objectTypes" :key="type.code" class="admin-tab-item"
                :class="{ active: activeTab === type.code }" @click="activeTab = type.code">
                {{ type.name }}
            </button>
        </div>

        <div class="tab-content">
            <div v-if="loading" class="loading-state">Đang tải dữ liệu...</div>
            <div v-else class="ui-table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th v-if="auth.isSuperuser" width="40">
                                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
                            </th>
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
                        <tr v-for="item in items" :key="item.id"
                            :class="{ 'row-selected': selectedIds.includes(item.id) }">
                            <td v-if="auth.isSuperuser">
                                <input type="checkbox" :checked="selectedIds.includes(item.id)"
                                    @change="toggleSelect(item.id)" />
                            </td>
                            <td>
                                {{ item.id }}
                                <div v-if="item.profiles_count === 0"
                                    class="inline-block px-1 py-0.5 rounded text-xs bg-orange-100 text-orange-600 border border-orange-200 mt-1 font-bold">
                                    Chưa liên kết</div>
                            </td>
                            <td class="font-bold">
                                <!-- Hiển thị tên hoặc số GCN tùy loại, hoặc fallback display_name -->
                                {{ item.ho_ten || item.so_giay_chung_nhan || item.display_name || '---' }}
                            </td>
                            <td>
                                <span>{{ getDynamicSummary(item, activeTab) }}</span>
                            </td>
                            <td>{{ formatDate(item.created_at) }}</td>
                            <td>
                                <div class="text-sm">
                                    <div>{{ formatDate(item.updated_at) }}</div>
                                    <small class="inline-block px-1 bg-gray-100 text-gray-600 rounded bg-gray-100"
                                        v-if="item.last_updated_by_name">
                                        👤 {{ item.last_updated_by_name }}
                                    </small>
                                </div>
                            </td>
                            <td>
                                <div class="flex gap-2">
                                    <button class="btn-action btn-secondary" @click="viewRelated(item)">Liên
                                        kết</button>
                                    <button class="btn-action btn-edit" @click="editObject(item)">Sửa</button>
                                    <button class="btn-action btn-delete" @click="confirmDelete(item)">Xóa</button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- RELATED INFO MODAL -->
        <div v-if="showRelatedModal" class="admin-modal-overlay" @click.self="showRelatedModal = false">
            <div class="admin-side-modal" :style="{ width: sideModalWidth + 'px' }">
                <!-- RESIZE HANDLE -->
                <div class="resizer-handle" @mousedown="startResize"></div>

                <div class="side-modal-header">
                    <h3>{{ relatedTitle }}</h3>
                    <button class="side-modal-close" @click="showRelatedModal = false">&times;</button>
                </div>

                <div class="side-modal-tabs">
                    <button class="side-modal-tab-btn" :class="{ active: relatedTab === 'profiles' }"
                        @click="relatedTab = 'profiles'">
                        Hồ sơ ({{ relatedProfiles.length }})
                    </button>
                    <button v-if="relatedType === 'PERSON'" class="side-modal-tab-btn"
                        :class="{ active: relatedTab === 'assets' }" @click="relatedTab = 'assets'">
                        Tài sản ({{ relatedAssets.length }})
                    </button>
                    <button v-if="relatedType !== 'PERSON'" class="side-modal-tab-btn"
                        :class="{ active: relatedTab === 'owners' }" @click="relatedTab = 'owners'">
                        Chủ sở hữu ({{ owners.length }})
                    </button>
                </div>

                <div class="side-modal-body">
                    <div v-if="relatedLoading" class="text-center p-8 text-gray-500">
                        <span class="inline-block animate-spin mr-2">⏳</span> Đang tải...
                    </div>
                    <div v-else>
                        <!-- CONTENT: PROFILES -->
                        <div v-if="relatedTab === 'profiles'">
                            <div v-for="item in relatedProfiles" :key="item.id" class="side-detail-item">
                                <div class="font-bold mb-1 text-slate-700">📄 {{ item.name }}</div>
                                <div class="text-sm text-gray-500 mb-3">
                                    <span>Loại: {{ item.form_name }}</span> |
                                    <span>Ngày: {{ formatDate(item.created_at) }}</span>
                                </div>
                                <button class="btn-action btn-secondary w-full" @click="goToProfile(item.id)">Mở Hồ
                                    sơ</button>
                            </div>
                            <div v-if="relatedProfiles.length === 0" class="text-center text-gray-400 p-8">
                                Chưa có hồ sơ liên quan.
                            </div>
                        </div>

                        <!-- CONTENT: ASSETS (For Person) -->
                        <div v-if="relatedTab === 'assets'">
                            <div v-for="rel in relatedAssets" :key="rel.id" class="side-detail-item">
                                <div class="font-bold mb-1 text-slate-700">🏠 {{ rel.target_name }}</div>
                                <div class="text-sm text-gray-500 mb-3">
                                    <span>Loại: {{ rel.target_type }}</span> |
                                    <span>Quan hệ: {{ rel.relation_type }}</span>
                                </div>
                                <button class="btn-action btn-secondary w-full"
                                    @click="viewChildDetails(rel.target_object)">Xem chi
                                    tiết</button>
                            </div>
                            <div v-if="relatedAssets.length === 0" class="text-center text-gray-400 p-8">
                                Chưa sở hữu tài sản nào.
                            </div>
                        </div>

                        <!-- CONTENT: OWNERS (For Assets) -->
                        <div v-if="relatedTab === 'owners'">
                            <div v-for="rel in owners" :key="rel.id" class="side-detail-item">
                                <div class="font-bold mb-1 text-slate-700">👤 {{ rel.source_name }}</div>
                                <div class="text-sm text-gray-500 mb-3">
                                    <span>Quan hệ: {{ rel.relation_type }}</span>
                                </div>
                                <button class="btn-action btn-secondary w-full"
                                    @click="viewChildDetails(rel.source_object)">Xem chi
                                    tiết</button>
                            </div>
                            <div v-if="owners.length === 0" class="text-center text-gray-400 p-8">
                                Chưa xác định chủ sở hữu.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Confirm Delete Modal -->
        <ConfirmModal :visible="showDeleteModal" title="Xác nhận xóa"
            :message="`Bạn có chắc muốn xóa đối tượng này? Thao tác này sẽ gỡ liên kết khỏi các hồ sơ cũ nhưng không xóa dữ liệu trong hồ sơ.`"
            confirmText="Xóa" @confirm="executeDelete" @cancel="showDeleteModal = false" />

        <!-- Bulk Delete Modal -->
        <ConfirmModal :visible="showBulkDeleteModal" type="warning" title="Xóa hàng loạt"
            :message="`Bạn có chắc chắn muốn xóa ${selectedIds.length} đối tượng đã chọn? Hành động này sẽ gỡ liên kết khỏi các hồ sơ cũ nhưng không xóa dữ liệu thực tế trong hồ sơ.`"
            confirmText="Xác nhận xóa" @confirm="executeBulkDelete" @cancel="showBulkDeleteModal = false" />

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

        <!-- CREATE/EDIT MODAL -->
        <MasterCreateModal :isOpen="showCreateModal" :type="tempOverrideType || activeTab"
            :typeName="tempOverrideTypeName || currentTypeName" :editObject="targetEditObject"
            @close="showCreateModal = false" @success="fetchData" />
    </div>
</template>

<script>
import axios from 'axios';
import auth from '@/store/auth';
import SvgIcon from '@/components/common/SvgIcon.vue';
import ConfirmModal from '../../components/ConfirmModal.vue';
import MasterCreateModal from '../../components/MasterCreateModal.vue';
import { makeTableResizable } from '../../utils/resizable-table';
import { errorHandlingMixin } from '../../utils/errorHandler';

export default {
    name: 'MasterData',
    components: { ConfirmModal, MasterCreateModal, SvgIcon },
    mixins: [errorHandlingMixin],
    data() {
        return {
            objectTypes: [], // List of dynamic types
            activeTab: '', // Code of active type
            loading: false,
            items: [], // Unified list for the current tab
            selectedIds: [], // Selected IDs for bulk actions
            auth, // Auth store for role checking

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
            showBulkDeleteModal: false,
            deleteTarget: null,
            // deleteTargetType: '', // Không cần nữa, dùng activeTab code

            // Create/Edit
            showCreateModal: false,
            targetEditObject: null,

            // Resizing (cleaned up)
            sideModalWidth: 500,
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
        },
        isAllSelected() {
            return this.items.length > 0 && this.selectedIds.length === this.items.length;
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
        getDynamicSummary(item, typeCode) {
            const typeDef = this.objectTypes.find(t => t.code === typeCode);
            if (!typeDef || !typeDef.dynamic_summary_template) {
                // Fallback cũ nếu không có cấu hình template
                if (typeCode === 'PERSON') return item.cccd ? `CCCD: ${item.cccd}` : '---';
                if (typeCode === 'ATTORNEY') return item.nguoi_dai_dien || '---';
                return item.owner_name || '---';
            }

            let result = typeDef.dynamic_summary_template;
            // Thay thế các placeholder {key} bằng giá trị thực
            const placeholders = result.match(/{([^}]+)}/g);
            if (placeholders) {
                placeholders.forEach(ph => {
                    const key = ph.slice(1, -1);
                    const val = item[key] !== undefined ? item[key] : '...';
                    result = result.replace(ph, val);
                });
            }
            return result;
        },
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
            this.selectedIds = []; // Clear selection when fetching/changing tab
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
                this.showSuccess('Đã xóa thành công!');
            } catch (error) {
                this.showError(error, 'Lỗi khi xóa');
            }
        },
        // Bulk Selection Logic
        toggleSelect(id) {
            const index = this.selectedIds.indexOf(id);
            if (index === -1) {
                this.selectedIds.push(id);
            } else {
                this.selectedIds.splice(index, 1);
            }
        },
        toggleSelectAll() {
            if (this.isAllSelected) {
                this.selectedIds = [];
            } else {
                this.selectedIds = this.items.map(item => item.id);
            }
        },
        confirmBulkDelete() {
            this.showBulkDeleteModal = true;
        },
        async executeBulkDelete() {
            try {
                this.loading = true;
                await axios.post('http://127.0.0.1:8000/api/master-objects/bulk-delete/', {
                    ids: this.selectedIds
                });
                this.showBulkDeleteModal = false;
                this.selectedIds = [];
                await this.fetchData();
                this.showSuccess('Đã xóa hàng loạt thành công!');
            } catch (error) {
                this.showError(error, 'Lỗi khi xóa hàng loạt');
            } finally {
                this.loading = false;
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
/* Resizer Handle specific style since it's interaction-heavy */
.resizer-handle {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
    cursor: col-resize;
    z-index: 10;
    transition: background 0.2s;
}

.resizer-handle:hover {
    background: rgba(59, 130, 246, 0.2);
    /* color-primary with opacity */
}
</style>

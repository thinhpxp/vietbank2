<template>
    <div class="admin-page page-container">
        <div class="page-header">
            <h2>Quản lý Dữ liệu gốc (Master Data)</h2>
            <div class="flex gap-2">
                <button v-if="auth.isSuperuser && selectedIds.length > 0" class="btn-action btn-danger"
                    @click="confirmBulkDelete">
                    <SvgIcon name="trash" size="sm" /> Xóa hàng loạt ({{ selectedIds.length }})
                </button>
                <button class="btn-action btn-refresh btn-icon-only" @click="fetchData" :disabled="loading"
                    title="Làm mới">
                    <SvgIcon name="refresh" size="sm" :class="{ 'animate-spin': loading }" />
                </button>
                <button class="btn-action btn-create btn-icon-only" @click="openCreateModal()"
                    title="Thêm mới đối tượng">
                    <SvgIcon name="plus" size="sm" />
                </button>
            </div>
        </div>

        <!-- Filter Bar -->
        <div class="filter-bar mb-4">
            <div class="filter-group">
                <label>Tìm kiếm:</label>
                <input v-model="filters.search" placeholder="Tìm theo tên, số hiệu..." class="admin-form-control"
                    style="width: 300px">
            </div>
            <div v-if="editingLockedBy" class="indicator-tag indicator-danger ml-auto">
                ⚠️ Hệ thống đang ở chế độ xem. Đối tượng đang bị khóa bởi: {{ editingLockedBy }}
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
            <div v-else class="data-table-vxe">
                <vxe-table border round :data="filteredItems" :row-config="{ isHover: true }"
                    :column-config="{ resizable: true }"
                    :sort-config="{ trigger: 'cell', defaultSort: { field: 'id', order: 'desc' } }"
                    @checkbox-change="handleCheckboxChange" @checkbox-all="handleCheckboxAll">

                    <vxe-column v-if="auth.isSuperuser" type="checkbox" width="50"></vxe-column>

                    <vxe-column field="id" title="ID" width="120" sortable>
                        <template #default="{ row }">
                            {{ row.id }}
                            <div v-if="row.profiles_count === 0" class="indicator-tag indicator-warning mt-1">
                                Chưa liên kết</div>
                        </template>
                    </vxe-column>

                    <vxe-column field="display_name" title="Tên / Số hiệu" width="300" sortable>
                        <template #default="{ row }">
                            <span class="font-bold">
                                {{ row.ho_ten || row.so_giay_chung_nhan || $t(row.display_name) || '---' }}
                            </span>
                        </template>
                    </vxe-column>

                    <vxe-column title="Thông tin thêm" width="350">
                        <template #default="{ row }">
                            {{ getDynamicSummary(row, activeTab) }}
                        </template>
                    </vxe-column>

                    <vxe-column field="created_at" title="Ngày tạo" width="160" sortable>
                        <template #default="{ row }">
                            {{ formatDate(row.created_at) }}
                        </template>
                    </vxe-column>

                    <vxe-column field="updated_at" title="Cập nhật gần nhất" width="180" sortable>
                        <template #default="{ row }">
                            <div class="text-sm">
                                <div>{{ formatDate(row.updated_at) }}</div>
                                <small class="badge bg-gray-100 text-gray-600 mt-1" v-if="row.last_updated_by_name">
                                    👤 {{ row.last_updated_by_name }}
                                </small>
                            </div>
                        </template>
                    </vxe-column>

                    <vxe-column title="Hành động" width="250" fixed="right">
                        <template #default="{ row }">
                            <div class="flex gap-2">
                                <button class="btn-action btn-secondary btn-icon-only" @click="viewRelated(row)"
                                    title="Xem liên kết">
                                    <SvgIcon name="users" size="sm" />
                                </button>
                                <button class="btn-action btn-edit btn-icon-only" @click="editObject(row)" title="Sửa">
                                    <SvgIcon name="edit" size="sm" />
                                </button>
                                <button class="btn-action btn-delete btn-icon-only" @click="confirmDelete(row)"
                                    title="Xóa">
                                    <SvgIcon name="trash" size="sm" />
                                </button>
                            </div>
                        </template>
                    </vxe-column>
                </vxe-table>
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

                <!-- REMOVAL OF TABS: GOING UNIFIED -->
                <!-- <div class="side-modal-tabs">
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
                </div> -->


                <div class="side-modal-body unified-side-body">
                    <div v-if="relatedLoading" class="text-center p-8 text-gray-500">
                        <span class="inline-block animate-spin mr-2">⏳</span> Đвязаt tải...
                    </div>
                    <div v-else class="side-content-sections">
                        <!-- SECTION 1: PROFILES -->
                        <div class="side-section">
                            <h4 class="section-title">
                                <SvgIcon name="file-text" size="xs" /> Hồ sơ liên quan ({{
                                    relatedProfiles.length }})
                            </h4>
                            <div v-if="relatedProfiles.length === 0" class="empty-mini">Chưa có hồ sơ liên quan.</div>
                            <div v-for="item in relatedProfiles" :key="'p-' + item.id"
                                class="side-compact-card clickable-card" @click="goToProfile(item.id)">
                                <div class="card-main">
                                    <div class="font-bold text-slate-700">📄 {{ item.name }}</div>
                                    <div class="text-xs text-gray-500">
                                        {{ item.form_name }} | {{ $t(item.status) }} | {{ formatDate(item.created_at) }}
                                    </div>

                                </div>
                            </div>


                        </div>

                        <!-- SECTION 2: OWNERSHIP (Highlighted) -->
                        <div class="side-section highlight-section" v-if="ownershipRelations.length > 0">
                            <h4 class="section-title">
                                <SvgIcon name="shield" size="xs" /> Thông tin Sở hữu ({{
                                    ownershipRelations.length }})
                            </h4>
                            <div v-for="rel in ownershipRelations" :key="'own-' + rel.id"
                                class="side-compact-card clickable-card"
                                @click="viewChildDetails(rel.isSource ? rel.target_object : rel.source_object)">
                                <div class="card-main">
                                    <div class="flex items-center gap-2">
                                        <span class="font-bold text-slate-800">
                                            {{ rel.isSource ? (rel.target_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                                $t(rel.target_name) : (rel.source_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                                $t(rel.source_name) }}
                                        </span>

                                        <span class="badge-role">CHỦ SỞ HỮU</span>
                                    </div>
                                    <div class="text-xs text-gray-500">
                                        {{ rel.isSource ? 'Liên kết tới' : 'Cung cấp bởi' }} | {{ $t(rel.isSource ?
                                            rel.target_type : rel.source_type) }}
                                    </div>

                                </div>
                            </div>
                        </div>


                        <!-- SECTION 3: OTHER RELATIONS -->
                        <div class="side-section">
                            <h4 class="section-title">
                                <SvgIcon name="share-2" size="xs" /> Các liên kết khác ({{
                                    otherRelations.length }})
                            </h4>
                            <div v-if="otherRelations.length === 0 && ownershipRelations.length === 0"
                                class="empty-mini">
                                Không có liên kết đối tượng.
                            </div>
                            <div v-for="rel in otherRelations" :key="'other-' + rel.id"
                                class="side-compact-card clickable-card"
                                @click="viewChildDetails(rel.isSource ? rel.target_object : rel.source_object)">
                                <div class="card-main">
                                    <div class="font-bold text-slate-700">
                                        {{ rel.isSource ? (rel.target_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                            $t(rel.target_name) : (rel.source_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                            $t(rel.source_name) }}
                                    </div>

                                    <div class="text-xs text-gray-500 flex items-center gap-1">
                                        <span class="badge-relation">{{ $t(rel.relation_type) }}</span>
                                        <span>| {{ $t(rel.isSource ? rel.target_type : rel.source_type)
                                            }}</span>
                                    </div>

                                </div>
                            </div>
                        </div>

                        <!-- SECTION 4: AUDIT HISTORY -->
                        <div class="side-section">
                            <h4 class="section-title">
                                <SvgIcon name="clock" size="xs" /> Lịch sử thay đổi ({{ auditLogs.length }})
                            </h4>
                            <div v-if="auditLogs.length === 0" class="empty-mini">Chưa có lịch sử thay đổi.</div>
                            <div class="audit-timeline">
                                <div v-for="log in auditLogs" :key="log.id" class="audit-item">
                                    <div class="audit-meta">
                                        <span class="audit-user">👤 {{ log.user_name }}</span>
                                        <span class="audit-time">{{ formatDate(log.timestamp) }}</span>
                                    </div>
                                    <div class="audit-action" :class="log.action.toLowerCase()">
                                        {{ log.action_display }}
                                    </div>
                                    <div v-if="log.details" class="audit-details">
                                        <pre>{{ log.details }}</pre>
                                    </div>
                                </div>
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
            :readOnly="!!editingLockedBy" :key="targetEditObject ? targetEditObject.id : 'new'" @close="closeEditModal"
            @success="fetchData" />
    </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import auth from '@/store/auth';
import SvgIcon from '@/components/common/SvgIcon.vue';
import ConfirmModal from '../../components/ConfirmModal.vue';
import MasterCreateModal from '../../components/MasterCreateModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
    name: 'MasterData',
    components: { ConfirmModal, MasterCreateModal, SvgIcon },
    mixins: [errorHandlingMixin, FilterableTableMixin],
    data() {
        return {
            objectTypes: [], // List of dynamic types
            activeTab: '', // Code of active type
            loading: false,
            items: [], // Unified list for the current tab
            selectedIds: [], // Selected IDs for bulk actions
            auth, // Auth store for role checking

            // Filtering
            filters: {
                search: ''
            },

            // Related Modal
            showRelatedModal: false,
            relatedType: '', // PERSON or other
            relatedTitle: '',
            // Data buckets (Unified)
            relatedProfiles: [],
            ownershipRelations: [],
            otherRelations: [],


            relatedLoading: false,

            // Delete
            showDeleteModal: false,
            targetDeleteObject: null,
            showBulkDeleteModal: false,

            // Edit
            showCreateModal: false,
            targetEditObject: null,
            tempOverrideType: '',
            tempOverrideTypeName: '',

            // Audit Logs
            auditLogs: [],

            // Locking
            heartbeatInterval: null,
            editingLockedBy: null // If someone else is editing
        };
    },
    computed: {
        filteredItems() {
            // Define searchable fields based on type
            let searchFields = ['ho_ten', 'so_giay_chung_nhan', 'display_name'];

            return this.filterArray(this.items, this.filters, {
                search: { type: 'text', fields: searchFields }
            });
        },
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
    },
    beforeUnmount() {
        this.stopHeartbeat();
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
                const res = await axios.get(`${API_URL}/object-types/`);
                this.objectTypes = res.data;
                if (this.objectTypes.length > 0) {
                    this.activeTab = this.objectTypes[0].code;
                }
            } catch (e) {
                this.showError(e, 'Lỗi tải loại đối tượng');
            }
        },
        async fetchData() {
            if (!this.activeTab) return;
            this.loading = true;
            this.selectedIds = []; // Clear selection when fetching/changing tab
            try {
                const response = await axios.get(`${API_URL}/master-objects/?object_type=${this.activeTab}`);

                // Flatten
                this.items = response.data.map(item => ({
                    ...item,
                    ...item.field_values
                }));

            } catch (error) {
                this.showError(error, 'Lỗi khi tải dữ liệu master');
            } finally {
                this.loading = false;
            }
        },
        async viewRelated(obj) {
            this.showRelatedModal = true;
            this.relatedLoading = true;
            this.relatedType = obj.object_type; // PERSON, ASSET, etc.
            this.relatedTitle = `Thông tin liên quan: ${obj.ho_ten || obj.display_name}`;
            this.relatedTab = 'profiles'; // Reset tab

            try {
                // 2. Fetch Master Relations (Categorized & Deduplicated)
                const resDetail = await axios.get(`${API_URL}/master-objects/${obj.id}/`);
                const detail = resDetail.data;

                const allRelsRaw = [];
                // Add relations where this object is Source (out)
                if (detail.relations_out) {
                    detail.relations_out.forEach(r => allRelsRaw.push({ ...r, isSource: true }));
                }
                // Add relations where this object is Target (in)
                if (detail.relations_in) {
                    detail.relations_in.forEach(r => allRelsRaw.push({ ...r, isSource: false }));
                }

                const uniqueRelsMap = new Map();
                allRelsRaw.forEach(r => {
                    if (!uniqueRelsMap.has(r.id)) {
                        uniqueRelsMap.set(r.id, r);
                    }
                });
                const allRels = Array.from(uniqueRelsMap.values());

                this.ownershipRelations = allRels.filter(r => r.relation_type === 'OWNER');
                this.otherRelations = allRels.filter(r => r.relation_type !== 'OWNER');
                this.relatedProfiles = detail.related_profiles || [];

                // 3. Fetch Audit Logs
                const logRes = await axios.get(`${API_URL}/audit-logs/`, {
                    params: {
                        target_model: `MasterObject:${obj.object_type}`,
                        target_id: obj.id
                    }
                });
                this.auditLogs = logRes.data.results || logRes.data;

            } catch (error) {
                this.showError(error, 'Lỗi khi tải dữ liệu liên quan');
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
                await axios.delete(`${API_URL}/master-objects/${this.deleteTarget.id}/`);
                this.showDeleteModal = false;
                this.fetchData();
                this.$toast.success('Đã xóa thành công!');
            } catch (error) {
                this.showDeleteModal = false;
                this.showError(error, 'Lỗi khi xóa');
            }
        },
        handleCheckboxChange({ selection }) {
            this.selectedIds = (selection || []).map(row => row.id);
        },
        handleCheckboxAll({ selection }) {
            this.selectedIds = (selection || []).map(row => row.id);
        },
        confirmBulkDelete() {
            this.showBulkDeleteModal = true;
        },
        async executeBulkDelete() {
            try {
                this.loading = true;
                await axios.post(`${API_URL}/master-objects/bulk-delete/`, {
                    ids: this.selectedIds
                });
                this.showBulkDeleteModal = false;
                this.selectedIds = [];
                await this.fetchData();
                this.$toast.success('Đã xóa hàng loạt thành công!');
            } catch (error) {
                this.showBulkDeleteModal = false;
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
        async editObject(obj) {
            this.tempOverrideType = null;
            this.tempOverrideTypeName = null;
            this.editingLockedBy = null;

            try {
                // Toàn cục: thử lấy khóa (acquire lock)
                const lockRes = await axios.post(`${API_URL}/master-objects/${obj.id}/acquire_lock/`);
                if (lockRes.data.locked) {
                    this.editingLockedBy = lockRes.data.locked_by;
                } else {
                    this.startHeartbeat(obj.id);
                }
            } catch (e) {
                if (e.response && e.response.status === 423) {
                    this.editingLockedBy = e.response.data.locked_by;
                } else {
                    console.error("Lock error", e);
                }
            }

            this.targetEditObject = JSON.parse(JSON.stringify(obj));
            this.showCreateModal = true;
        },
        startHeartbeat(id) {
            this.stopHeartbeat();
            this.heartbeatInterval = setInterval(async () => {
                try {
                    await axios.post(`${API_URL}/master-objects/${id}/heartbeat/`);
                } catch (e) {
                    console.error("Heartbeat failed", e);
                    this.stopHeartbeat();
                }
            }, 300000); // 5 minutes
        },
        stopHeartbeat() {
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
                this.heartbeatInterval = null;
            }
        },
        async releaseLock(id) {
            try {
                await axios.post(`${API_URL}/master-objects/${id}/release_lock/`);
            } catch (e) {
                console.error("Release lock failed", e);
            }
        },
        closeEditModal() {
            if (this.targetEditObject && !this.editingLockedBy && this.showCreateModal) {
                this.releaseLock(this.targetEditObject.id);
            }
            this.stopHeartbeat();
            this.editingLockedBy = null;
            this.showCreateModal = false;
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
                const res = await axios.get(`${API_URL}/master-objects/${objectId}/`);
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
                this.showError(e, "Không thể tải thông tin chi tiết");
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
.tab-content {
    margin-top: 10px;
}

.row-selected {
    background-color: #eff6ff !important;
}

/* Custom override for unified side body */
.unified-side-body {
    padding: 0;
    background: #f8fafc;
}

.loading-state {
    text-align: center;
    padding: 60px;
    color: #94a3b8;
    font-style: italic;
}

/* Audit Timeline */
.audit-timeline {
    margin-top: 15px;
    border-left: 2px solid #e2e8f0;
    padding-left: 20px;
    max-height: 400px;
    overflow-y: auto;
}

.audit-item {
    position: relative;
    margin-bottom: 20px;
}

.audit-item::before {
    content: '';
    position: absolute;
    left: -26px;
    top: 5px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #94a3b8;
}

.audit-meta {
    font-size: 0.8rem;
    color: #64748b;
    margin-bottom: 4px;
}

.audit-user {
    font-weight: bold;
    margin-right: 10px;
}

.audit-time {
    float: right;
}

.audit-action {
    font-weight: bold;
    font-size: 0.9rem;
    text-transform: uppercase;
}

.audit-action.update {
    color: #3b82f6;
}

.audit-action.create {
    color: #10b981;
}

.audit-action.delete {
    color: #ef4444;
}

.audit-details pre {
    background: #f1f5f9;
    padding: 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    margin-top: 5px;
    white-space: pre-wrap;
    font-family: monospace;
    color: #475569;
}
</style>

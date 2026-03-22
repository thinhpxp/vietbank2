<template>
    <div class="admin-page">
        <div class="page-header">
            <h2>Quản lý Dữ liệu gốc (Master Data)</h2>
            <div class="flex gap-2">
                <button v-if="authStore.isSuperuser && selectedIds.length > 0" class="btn-action btn-delete"
                    @click="confirmBulkDelete">
                    <SvgIcon name="trash" size="sm" /> Xóa hàng loạt ({{ selectedIds.length }})
                </button>
                <button class="btn-action btn-refresh btn-icon-only" @click="fetchData" :disabled="loading"
                    title="Làm mới">
                    <SvgIcon name="refresh" size="sm" :class="{ 'animate-spin': loading }" />
                </button>
                <button class="btn-action btn-create btn-icon-only" @click="openCreateModal()"
                    :disabled="!authStore.hasPermission('document_automation.add_masterobject')"
                    :title="authStore.hasPermission('document_automation.add_masterobject') ? 'Thêm mới đối tượng' : 'Không có quyền tạo'">
                    <SvgIcon name="plus" size="sm" />
                </button>
            </div>
        </div>

        <div class="filter-bar admin-row align-end gap-md mb-4">
            <div class="filter-group" style="flex: 1; min-width: 300px;">
                <label class="premium-label">
                    <SvgIcon name="search" size="xs" /> Tìm kiếm
                </label>
                <div class="premium-input-wrapper">
                    <input v-model="filters.search" placeholder="Tìm theo tên, số hiệu..."
                        class="filter-control premium-input">
                </div>
            </div>

            <div class="filter-group" style="flex: 0 0 auto;">
                <label class="premium-label" style="visibility: hidden;">&nbsp;</label>
                <div class="premium-input-wrapper">
                    <button class="btn-action btn-secondary flex items-center gap-2" @click="resetFilters"
                        title="Đặt lại bộ lọc">
                        <SvgIcon name="x" size="sm" /> <span>Đặt lại</span>
                    </button>
                </div>
            </div>

            <div v-if="editingLockedBy" class="indicator-tag indicator-danger ml-auto mb-1">
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
                    :column-config="{ resizable: true }" :row-class-name="rowClassName"
                    :sort-config="{ trigger: 'cell', defaultSort: { field: 'id', order: 'desc' } }"
                    @checkbox-change="handleCheckboxChange" @checkbox-all="handleCheckboxAll">

                    <vxe-column v-if="authStore.isSuperuser" type="checkbox" width="50"></vxe-column>

                    <vxe-column field="id" title="ID" width="120" sortable>
                        <template #default="{ row }">
                            {{ row.id }}
                            <div v-if="row.profiles_count === 0" class="indicator-tag indicator-warning mt-1">
                                Chưa liên kết</div>
                        </template>
                    </vxe-column>

                    <vxe-column field="identity_value" title="Định danh / Số hiệu" width="300" sortable>
                        <template #default="{ row }">
                            <span class="font-bold">
                                {{ getIdentityValue(row) }}
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
                                <small class="admin-badge badge-inactive mt-1" v-if="row.last_updated_by_name">
                                    👤 {{ row.last_updated_by_name }}
                                </small>
                            </div>
                        </template>
                    </vxe-column>

                    <vxe-column title="Hành động" width="280" fixed="right">
                        <template #default="{ row }">
                            <div class="action-buttons-container">
                                <!-- Group: Actions for Active items -->
                                <template v-if="!row.is_deleted">
                                    <button class="btn-action btn-secondary btn-icon-only" @click="viewRelated(row)"
                                        title="Xem liên kết">
                                        <SvgIcon name="users" size="sm" />
                                    </button>
                                    <button class="btn-action btn-edit btn-icon-only" @click="editObject(row)"
                                        :disabled="!authStore.hasPermission('document_automation.change_masterobject')"
                                        :title="authStore.hasPermission('document_automation.change_masterobject') ? 'Sửa' : 'Không có quyền sửa'">
                                        <SvgIcon name="edit" size="sm" />
                                    </button>
                                    <button class="btn-action btn-delete btn-icon-only" @click="confirmDelete(row)"
                                        :disabled="!authStore.hasPermission('document_automation.delete_masterobject')"
                                        :title="authStore.hasPermission('document_automation.delete_masterobject') ? 'Xóa' : 'Không có quyền xóa'">
                                        <SvgIcon name="trash" size="sm" />
                                    </button>
                                </template>

                                <!-- Group: Actions for Deleted items (ROOT only) -->
                                <template v-else-if="authStore.isSuperuser">
                                    <button class="btn-action btn-secondary btn-icon-only" @click="viewRelated(row)"
                                        title="Xem liên kết">
                                        <SvgIcon name="users" size="sm" />
                                    </button>
                                    <button class="btn-action btn-restore btn-icon-only" @click="confirmRestore(row)" title="KHÔI PHỤC">
                                        <SvgIcon name="refresh-cw" size="sm" />
                                    </button>
                                    <button class="btn-action btn-hard-delete btn-icon-only" @click="confirmHardDelete(row)"
                                        title="XÓA VĨNH VIỄN">
                                        <SvgIcon name="trash-2" size="sm" />
                                    </button>
                                </template>
                            </div>
                        </template>
                    </vxe-column>
                </vxe-table>
            </div>
        </div>

        <!-- RELATED INFO MODAL -->
        <div v-if="showRelatedModal" class="admin-modal-overlay" @click.self="showRelatedModal = false">
            <div class="admin-side-modal" :class="{ resizing: isResizing }" :style="{ width: sideModalWidth + 'px' }">
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
                        <span class="inline-block animate-spin mr-2">⏳</span> Đang tải...
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
                                <div class="card-main" :class="{ 'row-deleted-blurred': item.is_deleted }">
                                    <div class="font-bold text-slate-700" :class="{ 'text-deleted': item.is_deleted }">
                                        📄 {{ item.name }}
                                        <span v-if="item.is_deleted" class="badge-role" style="background: #ef4444; color: white;">[ĐÃ XÓA]</span>
                                    </div>
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
                                @click="viewChildDetails(rel.isSource ? rel.target_object : rel.source_object, rel.isSource ? rel.target_is_deleted : rel.source_is_deleted)">
                                <div class="card-main" :class="{ 'row-deleted-blurred': rel.isSource ? rel.target_is_deleted : rel.source_is_deleted }">
                                    <div class="flex items-center gap-2">
                                        <span class="font-bold text-slate-800" :class="{ 'text-deleted': rel.isSource ? rel.target_is_deleted : rel.source_is_deleted }">
                                            {{ rel.isSource ? (rel.target_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                                rel.target_name : (rel.source_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                                rel.source_name }}
                                            <span v-if="rel.isSource ? rel.target_is_deleted : rel.source_is_deleted" 
                                                  class="badge-role" style="background: #ef4444; color: white; scale: 0.8;">[ĐÃ XÓA]</span>
                                            <span v-if="rel.isSource ? rel.target_additional_info : rel.source_additional_info"
                                                class="font-normal text-gray-500">
                                                | {{ rel.isSource ? rel.target_additional_info : rel.source_additional_info }}
                                            </span>
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
                                @click="viewChildDetails(rel.isSource ? rel.target_object : rel.source_object, rel.isSource ? rel.target_is_deleted : rel.source_is_deleted)">
                                <div class="card-main" :class="{ 'row-deleted-blurred': rel.isSource ? rel.target_is_deleted : rel.source_is_deleted }">
                                    <div class="font-bold text-slate-700" :class="{ 'text-deleted': rel.isSource ? rel.target_is_deleted : rel.source_is_deleted }">
                                        {{ rel.isSource ? (rel.target_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                            rel.target_name : (rel.source_type === 'PERSON' ? '👤 ' : '🏠 ') +
                                            rel.source_name }}
                                        <span v-if="rel.isSource ? rel.target_is_deleted : rel.source_is_deleted" 
                                              class="badge-role" style="background: #ef4444; color: white; scale: 0.8;">[ĐÃ XÓA]</span>
                                        <span v-if="rel.isSource ? rel.target_additional_info : rel.source_additional_info"
                                            class="font-normal text-gray-500">
                                            | {{ rel.isSource ? rel.target_additional_info : rel.source_additional_info }}
                                        </span>
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
            :readOnly="!!editingLockedBy || (targetEditObject && targetEditObject.is_deleted)" 
            :lockedBy="editingLockedBy"
            :key="targetEditObject ? targetEditObject.id : 'new'" @close="closeEditModal"
            @success="fetchData" />
    </div>
</template>

<script>
import MasterService from '@/services/master.service';
import SystemService from '@/services/system.service';
import { useAuthStore } from '@/store/auth.store';
import SvgIcon from '@/components/common/SvgIcon.vue';
import ConfirmModal from '../../components/ConfirmModal.vue';
import MasterCreateModal from '../../components/MasterCreateModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';
import eventBus, { EVENTS } from '@/utils/eventBus';

export default {
    name: 'MasterData',
    title: 'Quản lý Dữ liệu gốc',
    components: { ConfirmModal, MasterCreateModal, SvgIcon },
    mixins: [errorHandlingMixin, FilterableTableMixin],
    data() {
        return {
            objectTypes: [], // List of dynamic types
            activeTab: '', // Code of active type
            loading: false,
            items: [], // Unified list for the current tab
            selectedIds: [], // Selected IDs for bulk actions
            authStore: useAuthStore(), // Pinia store

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
            editingLockedBy: null, // If someone else is editing

            // UI Resizing
            sideModalWidth: 800,
            isResizing: false
        };
    },
    computed: {
        filteredItems() {
            // Define searchable fields based on type
            let searchFields = ['ho_ten', 'so_giay_chung_nhan', 'display_name', 'additional_info'];

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
        rowClassName({ row }) {
            if (row.is_deleted) return 'row-deleted-blurred';
            return '';
        },
        getIdentityValue(item) {
            const typeConfig = this.objectTypes.find(t => t.code === (item.object_type || this.activeTab));
            if (typeConfig && typeConfig.identity_field_key) {
                // Ưu tiên lấy từ field_values đã được flatten hoặc item trực tiếp
                return item[typeConfig.identity_field_key] || item.display_name || '---';
            }
            return item.display_name || '---';
        },
        getDynamicSummary(item, typeCode) {
            // Ưu tiên sử dụng thông tin đã được Backend xử lý theo template (Dynamic)
            if (item.additional_info) {
                return item.additional_info;
            }

            const typeDef = this.objectTypes.find(t => t.code === typeCode);
            if (!typeDef || !typeDef.dynamic_summary_template) {
                return '---';
            }

            // Tự render nếu chưa có additional_info từ API
            let result = typeDef.dynamic_summary_template;
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
                const res = await MasterService.getObjectTypes();
                // Lọc bỏ USER_EXT (ẩn với tất cả). BRANCH chỉ hiển thị với ROOT.
                this.objectTypes = res.data.filter(t => {
                    if (t.code === 'USER_EXT') return false;
                    if (t.code === 'BRANCH') return this.authStore.isSuperuser;
                    return true;
                });
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
                const response = await MasterService.getAllObjects({ object_type: this.activeTab });

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
            const name = obj.ho_ten || obj.display_name;
            const info = obj.additional_info ? ` | ${obj.additional_info}` : '';
            this.relatedTitle = `Thông tin liên quan: ${name}${info}`;
            this.relatedTab = 'profiles'; // Reset tab

            try {
                // 1. Fetch relations (Phase 10: support deleted objects via include_deleted)
                const params = obj.is_deleted ? { include_deleted: true } : {};
                const resDetail = await MasterService.getObjectById(obj.id, params);
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
                // Lọc quan hệ theo Whitelist hai chiều
                const allRels = Array.from(uniqueRelsMap.values()).filter(rel => {
                    const s_type = rel.source_type;
                    const t_type = rel.target_type;
                    const s_restricted = rel.source_is_restricted;
                    const t_restricted = rel.target_is_restricted;
                    const s_whitelist = rel.source_allowed_relation_types_codes || [];
                    const t_whitelist = rel.target_allowed_relation_types_codes || [];

                    // Rule for Source
                    if (s_restricted || s_whitelist.length > 0) {
                        if (!s_whitelist.includes(t_type)) return false;
                    }

                    // Rule for Target
                    if (t_restricted || t_whitelist.length > 0) {
                        if (!t_whitelist.includes(s_type)) return false;
                    }

                    return true;
                });

                this.ownershipRelations = allRels.filter(r => r.relation_type === 'OWNER');
                this.otherRelations = allRels.filter(r => r.relation_type !== 'OWNER');
                this.relatedProfiles = detail.related_profiles || [];

                // 3. Fetch Audit Logs
                const logRes = await SystemService.getAuditLogs({
                    target_model: `MasterObject:${obj.object_type}`,
                    target_id: obj.id
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
        confirmDelete(row) {
            eventBus.emit(EVENTS.SHOW_GLOBAL_CONFIRM, {
                title: 'Xác nhận xóa',
                message: `Bạn có chắc muốn xóa <b>${row.display_name}</b>? dữ liệu sẽ được chuyển sang trạng thái làm mờ.`,
                type: 'warning',
                showReason: true,
                onConfirm: (reason) => {
                    this.executeDelete(row.id, reason);
                }
            });
        },
        async executeDelete(id, reason) {
            try {
                this.loading = true;
                await MasterService.deleteObject(id, reason);
                this.$toast.success('Đã xóa thành công!');
                await this.fetchData();
            } catch (error) {
                this.showError(error, 'Lỗi khi xóa');
            } finally {
                this.loading = false;
            }
        },
        async confirmRestore(row) {
            eventBus.emit(EVENTS.SHOW_GLOBAL_CONFIRM, {
                title: 'KHÔI PHỤC ĐỐI TƯỢNG',
                message: `Bạn có chắc chắn muốn khôi phục <b>${row.display_name}</b>? dữ liệu sẽ quay lại trạng thái hoạt động bình thường.`,
                type: 'success',
                showReason: false,
                onConfirm: async () => {
                    try {
                        this.loading = true;
                        await MasterService.restoreObject(row.id);
                        this.$toast.success('Đã khôi phục thành công!');
                        await this.fetchData();
                    } catch (e) {
                        this.showError(e, 'Lỗi khi khôi phục');
                    } finally {
                        this.loading = false;
                    }
                }
            });
        },
        confirmHardDelete(row) {
            eventBus.emit(EVENTS.SHOW_GLOBAL_CONFIRM, {
                title: 'XÓA VĨNH VIỄN',
                message: `<div class="alert alert-danger">⚠️ <b>CẢNH BÁO:</b> Đối tượng <b>${row.display_name}</b> sẽ bị xóa VĨNH VIỄN khỏi hệ thống cùng với mọi liên kết lịch sử. Hành động này không thể hoàn tác!</div>`,
                type: 'error',
                showReason: true,
                reasonLabel: 'Lý do xóa vĩnh viễn (Phải có):',
                onConfirm: async (reason) => {
                    if (!reason) {
                        this.$toast.warning('Yêu cầu nhập lý do xóa vĩnh viễn');
                        return;
                    }
                    try {
                        this.loading = true;
                        // Lưu lý do qua Audit Log thủ công hoặc Backend tự log
                        await MasterService.hardDeleteObject(row.id);
                        this.$toast.success('Đã xóa vĩnh viễn!');
                        await this.fetchData();
                    } catch (e) {
                        this.showError(e, 'Lỗi xóa vĩnh viễn');
                    } finally {
                        this.loading = false;
                    }
                }
            });
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
                await MasterService.bulkDeleteObjects(this.selectedIds);
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
                const lockRes = await MasterService.acquireLock(obj.id);
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
                    await MasterService.heartbeat(id);
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
                await MasterService.releaseLock(id);
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
        async viewChildDetails(objectId, isDeleted = false) {
            // Fetch full details of the child object then open modal
            try {
                this.relatedLoading = true;
                const params = isDeleted ? { include_deleted: true } : {};
                const res = await MasterService.getObjectById(objectId, params);
                // Flatten fields like we do in fetchData
                const fullObj = {
                    ...res.data,
                    ...res.data.field_values
                };

                // Determine type title for the modal
                const typeCode = fullObj.object_type;
                const typeDef = this.objectTypes.find(t => t.code === typeCode);
                const typeName = typeDef ? typeDef.name : typeCode;

                // LOCKING LOGIC: Try to acquire lock for this object
                this.editingLockedBy = null;
                try {
                    const lockRes = await MasterService.acquireLock(objectId);
                    if (lockRes.data.locked) {
                        this.editingLockedBy = lockRes.data.locked_by;
                    } else {
                        this.startHeartbeat(objectId);
                    }
                } catch (e) {
                    if (e.response && e.response.status === 423) {
                        this.editingLockedBy = e.response.data.locked_by;
                    } else {
                        console.error("Lock error", e);
                    }
                }

                // Reuse specific properties for this case
                this.targetEditObject = fullObj;
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
/* Redundant styles moved to admin.css */
.tab-content {
    margin-top: 10px;
}

/* Custom override for unified side body */
.unified-side-body {
    padding: 20px;
    background: var(--slate-50);
}


/* Soft Delete styles are now globally defined in common-ui.css */
.text-deleted {
    text-decoration: line-through;
    opacity: 0.6;
}
</style>

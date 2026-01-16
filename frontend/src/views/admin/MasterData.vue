<template>
    <div class="admin-page">
        <div class="flex justify-between items-center mb-6">
            <h2>Quản lý Dữ liệu gốc (Master Data)</h2>
            <div class="flex gap-2">
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
                            <div v-if="item.profiles_count === 0" class="inline-block px-1 py-0.5 rounded text-xs bg-orange-100 text-orange-600 border border-orange-200 mt-1 font-bold">Chưa liên kết</div>
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
                            <div class="text-sm">
                                <div>{{ formatDate(item.updated_at) }}</div>
                                <small class="inline-block px-1 bg-gray-100 text-gray-600 rounded bg-gray-100" v-if="item.last_updated_by_name">
                                    👤 {{ item.last_updated_by_name }}
                                </small>
                            </div>
                        </td>
                        <td>
                            <div class="flex gap-2">
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
        <div v-if="showRelatedModal" class="admin-modal-overlay" @click.self="showRelatedModal = false">
            <div class="admin-side-modal" :style="{ width: sideModalWidth + 'px' }">
                <!-- RESIZE HANDLE -->
                <div class="resizer-handle" @mousedown="startResize"></div>

                <div class="flex justify-between items-center p-4 border-b">
                    <h3>{{ relatedTitle }}</h3>
                    <button class="text-2xl" @click="showRelatedModal = false">&times;</button>
                </div>
                <div class="flex-1 overflow-y-auto p-4">
                    <div v-if="relatedLoading">Đang tải...</div>
                    <div v-else>
                        <!-- TABS IN MODAL -->
                        <div class="flex gap-2 mb-4 border-b pb-2">
                            <button class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 text-gray-700 font-medium" :class="{ 'bg-blue-100 text-blue-700': relatedTab === 'profiles' }" @click="relatedTab = 'profiles'">Hồ
                                sơ
                                ({{ relatedProfiles.length }})</button>
                            <button v-if="relatedType === 'PERSON'" class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 text-gray-700 font-medium" :class="{ 'bg-blue-100 text-blue-700': relatedTab === 'assets' }"
                                @click="relatedTab = 'assets'">Tài sản ({{ relatedAssets.length }})</button>
                            <button v-if="relatedType !== 'PERSON'" class="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 text-gray-700 font-medium" :class="{ 'bg-blue-100 text-blue-700': relatedTab === 'owners' }"
                                @click="relatedTab = 'owners'">Chủ sở hữu ({{ owners.length }})</button>
                        </div>

                        <!-- CONTENT: PROFILES -->
                        <ul v-if="relatedTab === 'profiles'" class="list-none p-0">
                            <li v-for="item in relatedProfiles" :key="item.id" class="p-4 border border-gray-100 rounded mb-2 bg-gray-50">
                                <div class="font-bold mb-1">📄 {{ item.name }}</div>
                                <div class="text-sm text-gray-500 mb-2">
                                    <span>Loại: {{ item.form_name }}</span> |
                                    <span>Ngày: {{ formatDate(item.created_at) }}</span>
                                </div>
                                <button class="btn-action btn-secondary" @click="goToProfile(item.id)">Mở Hồ sơ</button>
                            </li>
                            <li v-if="relatedProfiles.length === 0" class="text-center text-gray-400 p-4">Chưa có hồ sơ liên quan.</li>
                        </ul>

                        <!-- CONTENT: ASSETS (For Person) -->
                        <ul v-if="relatedTab === 'assets'" class="list-none p-0">
                            <li v-for="rel in relatedAssets" :key="rel.id" class="p-4 border border-gray-100 rounded mb-2 bg-gray-50">
                                <div class="font-bold mb-1">🏠 {{ rel.target_name }}</div>
                                <div class="text-sm text-gray-500 mb-2">
                                    <span>Loại: {{ rel.target_type }}</span> |
                                    <span>Quan hệ: {{ rel.relation_type }}</span>
                                </div>
                                <button class="btn-action btn-secondary" @click="viewChildDetails(rel.target_object)">Xem chi
                                    tiết</button>
                            </li>
                            <li v-if="relatedAssets.length === 0" class="text-center text-gray-400 p-4">Chưa sở hữu tài sản nào.</li>
                        </ul>

                        <!-- CONTENT: OWNERS (For Assets) -->
                        <ul v-if="relatedTab === 'owners'" class="list-none p-0">
                            <li v-for="rel in owners" :key="rel.id" class="p-4 border border-gray-100 rounded mb-2 bg-gray-50">
                                <div class="font-bold mb-1">👤 {{ rel.source_name }}</div>
                                <div class="text-sm text-gray-500 mb-2">
                                    <span>Quan hệ: {{ rel.relation_type }}</span>
                                </div>
                                <button class="btn-action btn-secondary" @click="viewChildDetails(rel.source_object)">Xem chi
                                    tiết</button>
                            </li>
                            <li v-if="owners.length === 0" class="text-center text-gray-400 p-4">Chưa xác định chủ sở hữu.</li>
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
    background: rgba(59, 130, 246, 0.2); /* color-primary with opacity */
}
</style>


<template>
    <div class="admin-page dashboard-container">
        <div class="header-actions flex justify-between items-center mb-4">
            <h2>Quản lý Loại Đối tượng (Object Types)</h2>
        </div>

        <!-- Add New Type Panel -->
        <div class="admin-panel mb-4">
            <h4 class="mb-3">Thêm loại đối tượng mới</h4>
            <!-- Row 1: Identity -->
            <div class="admin-row mb-2">
                <input v-model="newType.code" placeholder="Mã (Code) *" class="admin-input" style="max-width: 150px">
                <input v-model="newType.name" placeholder="Tên hiển thị *" class="admin-input" style="flex: 2">
                <input v-model="newType.identity_field_key" placeholder="Trường định danh (key)" class="admin-input">
            </div>

            <!-- Row 2: Config -->
            <div class="admin-row mb-2">
                <input v-model.number="newType.order" type="text" inputmode="numeric" placeholder="Thứ tự"
                    class="admin-input" style="max-width: 80px">

                <select v-model="newType.form_display_mode" class="admin-input" title="Kiểu hiển thị">
                    <option :value="null" disabled>- Kiểu đối tượng -</option>
                    <option value="ASSET_LIST">Đây là tài sản</option>
                    <option value="DEDICATED_SECTION">Đối tượng độc lập</option>
                </select>

                <select v-model="newType.layout_position" class="admin-input" title="Vị trí (Cột)"
                    style="max-width: 120px">
                    <option :value="null" disabled>- Vị trí -</option>
                    <option value="LEFT">Cột Trái</option>
                    <option value="RIGHT">Cột Phải</option>
                </select>

                <input v-model="newType.dynamic_summary_template"
                    placeholder="Thông tin hiển thị với người dùng,Ví dụ: CCCD {cccd}" class="admin-input"
                    style="flex: 2">
            </div>

            <!-- Row 3: Details & Action -->
            <div class="admin-row">
                <input v-model="newType.description" placeholder="Mô tả..." class="admin-input" style="flex: 1">

                <label class="admin-checkbox-label" style="white-space: nowrap; margin-right: 10px;">
                    <input type="checkbox" v-model="newType.allow_relations"> Cho phép liên kết đến đối tượng khác
                </label>

                <button @click="addType" class="btn-action btn-create">Thêm Loại</button>
            </div>
        </div>

        <div class="filter-bar mb-4">
            <div class="filter-group">
                <label>Tìm kiếm:</label>
                <input v-model="filters.search" placeholder="Tìm theo tên hoặc mã..." class="admin-form-control"
                    style="width: 300px">
            </div>
        </div>

        <div class="data-table-vxe">
            <vxe-table border round :data="filteredTypes" :row-config="{ isHover: true }"
                :column-config="{ resizable: true }" :sort-config="{ trigger: 'cell' }">

                <vxe-column field="code" title="Mã (Code)" width="150" sortable>
                    <template #default="{ row }">
                        <code>{{ row.code }}</code>
                    </template>
                </vxe-column>

                <vxe-column field="name" title="Tên hiển thị" width="200" sortable>
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="editingData.name" class="vxe-input-minimal" />
                        <span v-else class="font-bold">{{ row.name }}</span>
                    </template>
                </vxe-column>

                <vxe-column field="identity_field_key" title="Trường định danh" width="180">
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="editingData.identity_field_key"
                            class="vxe-input-minimal" />
                        <code v-else>{{ row.identity_field_key || '---' }}</code>
                    </template>
                </vxe-column>

                <vxe-column field="form_display_mode" title="Phân loại" width="150">
                    <template #default="{ row }">
                        <select v-if="editingId === row.id" v-model="editingData.form_display_mode"
                            class="vxe-input-minimal">
                            <option value="ASSET_LIST">Tài sản</option>
                            <option value="DEDICATED_SECTION">Độc lập</option>
                        </select>
                        <span v-else class="badge"
                            :class="row.form_display_mode === 'DEDICATED_SECTION' ? 'badge-primary' : 'badge-secondary'">
                            {{ getDisplayModeLabel(row.form_display_mode) }}
                        </span>
                    </template>
                </vxe-column>

                <vxe-column field="layout_position" title="Vị trí" width="100">
                    <template #default="{ row }">
                        <select v-if="editingId === row.id" v-model="editingData.layout_position"
                            class="vxe-input-minimal">
                            <option value="LEFT">Trái</option>
                            <option value="RIGHT">Phải</option>
                        </select>
                        <span v-else class="badge"
                            :class="row.layout_position === 'RIGHT' ? 'badge-primary' : 'badge-secondary'">
                            {{ row.layout_position === 'RIGHT' ? '👉 Phải' : '👈 Trái' }}
                        </span>
                    </template>
                </vxe-column>

                <vxe-column field="allow_relations" title="Cho phép LK" width="120">
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="editingData.allow_relations" type="checkbox" />
                        <span v-else class="badge" :class="row.allow_relations ? 'badge-success' : 'badge-secondary'">
                            {{ row.allow_relations ? '✓ Có' : '✗ Không' }}
                        </span>
                    </template>
                </vxe-column>

                <vxe-column field="dynamic_summary_template" title="Mẫu hiển thị" width="200">
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="editingData.dynamic_summary_template"
                            class="vxe-input-minimal" />
                        <span v-else>{{ row.dynamic_summary_template || '---' }}</span>
                    </template>
                </vxe-column>

                <vxe-column field="description" title="Mô tả" min-width="200">
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="editingData.description"
                            class="vxe-input-minimal" />
                        <span v-else>{{ row.description || '---' }}</span>
                    </template>
                </vxe-column>

                <vxe-column field="is_system" title="Hệ thống" width="100">
                    <template #default="{ row }">
                        <span v-if="row.is_system" class="badge badge-system">System</span>
                        <span v-else class="badge badge-custom">Custom</span>
                    </template>
                </vxe-column>

                <vxe-column field="order" title="Thứ tự" width="100" sortable>
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model.number="editingData.order" type="number"
                            class="vxe-input-minimal" />
                        <span v-else>{{ row.order }}</span>
                    </template>
                </vxe-column>

                <vxe-column title="Hành động" width="180" fixed="right">
                    <template #default="{ row }">
                        <div class="flex gap-2">
                            <template v-if="editingId === row.id">
                                <button class="btn-action btn-save" @click="updateType">Lưu</button>
                                <button class="btn-action btn-secondary" @click="editingId = null">Hủy</button>
                            </template>
                            <template v-else>
                                <button class="btn-action btn-edit" @click="startEdit(row)">Sửa</button>
                                <button class="btn-action btn-delete" :disabled="row.is_system"
                                    @click="confirmDelete(row)"
                                    :title="row.is_system ? 'Không thể xóa loại mặc định' : 'Xóa loại này'">
                                    Xóa
                                </button>
                            </template>
                        </div>
                    </template>
                </vxe-column>
            </vxe-table>
        </div>

        <!-- Confirm Delete -->
        <ConfirmModal :visible="showDeleteModal" title="Xóa Loại đối tượng"
            :message="`Bạn có chắc muốn xóa loại '${deleteTarget?.name}'? Các dữ liệu thuộc loại này có thể bị ảnh hưởng.`"
            confirmText="Xóa ngay" @confirm="executeDelete" @cancel="showDeleteModal = false" />

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
    </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import ConfirmModal from '../../components/ConfirmModal.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
    name: 'AdminObjectTypes',
    components: { ConfirmModal },
    mixins: [errorHandlingMixin, FilterableTableMixin],
    data() {
        return {
            types: [],
            newType: { code: '', name: '', description: '', identity_field_key: '', form_display_mode: null, layout_position: null, dynamic_summary_template: '', allow_relations: true, order: null },
            editingId: null,
            editingData: null,
            filters: { search: '' },
            showDeleteModal: false,
            deleteTarget: null
        };
    },
    computed: {
        filteredTypes() {
            return this.filterArray(this.types, this.filters, {
                search: { type: 'text', fields: ['name', 'code'] }
            });
        },
        sortedTypes() {
            return this.sortArray(this.filteredTypes);
        }
    },
    watch: {
    },
    mounted() {
        this.fetchTypes();
    },
    methods: {
        async fetchTypes() {
            try {
                const res = await axios.get(`${API_URL}/object-types/`);
                this.types = res.data;
            } catch (e) {
                this.showError(e, 'Lỗi tải danh sách loại đối tượng');
            }
        },
        getDisplayModeLabel(mode) {
            return mode === 'DEDICATED_SECTION' ? '📍 Độc lập' : '📦 Tài sản';
        },
        async addType() {
            if (!this.newType.code || !this.newType.name) {
                this.showWarning('Vui lòng nhập Mã và Tên', 'Thiếu thông tin');
                return;
            }
            try {
                await axios.post(`${API_URL}/object-types/`, this.newType);
                this.newType = { code: '', name: '', description: '', identity_field_key: '', form_display_mode: null, layout_position: null, dynamic_summary_template: '', order: null };
                this.fetchTypes();
            } catch (e) {
                this.showError(e, 'Lỗi khi thêm loại đối tượng');
            }
        },
        startEdit(item) {
            this.editingId = item.id;
            this.editingData = { ...item };
        },
        async updateType() {
            if (!this.editingData.name) {
                this.showWarning('Vui lòng nhập Tên hiển thị', 'Thiếu thông tin');
                return;
            }

            try {
                await axios.patch(`${API_URL}/object-types/${this.editingId}/`, this.editingData);
                this.editingId = null;
                this.fetchTypes();
            } catch (e) {
                this.showError(e, 'Lỗi khi cập nhật loại đối tượng');
            }
        },
        confirmDelete(item) {
            this.deleteTarget = item;
            this.showDeleteModal = true;
        },
        async executeDelete() {
            try {
                await axios.delete(`${API_URL}/object-types/${this.deleteTarget.id}/`);
                this.fetchTypes();
                this.showDeleteModal = false;
            } catch (e) {
                this.showDeleteModal = false;
                this.showError(e, 'Lỗi xóa');
            }
        }
    }
}
</script>

<style scoped>
.data-table-vxe {
    margin-top: 10px;
}
</style>

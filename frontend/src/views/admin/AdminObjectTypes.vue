<template>
    <div class="admin-page">
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

                <button @click="addType" class="btn-action btn-create btn-icon-only" :disabled="!canCreate"
                    :title="canCreate ? 'Thêm Loại đối tượng' : 'Không có quyền tạo'">
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
                    <input v-model="filters.search" placeholder="Tìm theo tên hoặc mã..."
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
                        <span v-else
                            :class="['admin-badge', row.form_display_mode === 'DEDICATED_SECTION' ? 'badge-active' : 'badge-inactive']">
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
                        <span v-else
                            :class="['admin-badge', row.layout_position === 'RIGHT' ? 'badge-active' : 'badge-inactive']">
                            {{ row.layout_position === 'RIGHT' ? '👉 Phải' : '👈 Trái' }}
                        </span>
                    </template>
                </vxe-column>

                <vxe-column field="allow_relations" title="Cho phép LK" width="120">
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model="editingData.allow_relations" type="checkbox" />
                        <span v-else :class="['admin-badge', row.allow_relations ? 'badge-active' : 'badge-inactive']">
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
                        <span v-if="row.is_system" class="admin-badge badge-admin">System</span>
                        <span v-else class="admin-badge badge-inactive">Custom</span>
                    </template>
                </vxe-column>

                <vxe-column field="order" title="Thứ tự" width="100" sortable>
                    <template #default="{ row }">
                        <input v-if="editingId === row.id" v-model.number="editingData.order" type="number"
                            class="vxe-input-minimal" />
                        <span v-else>{{ row.order }}</span>
                    </template>
                </vxe-column>

                <vxe-column title="Hành động" width="160" fixed="right">
                    <template #default="{ row }">
                        <div class="flex gap-2">
                            <template v-if="editingId === row.id">
                                <button class="btn-action btn-save btn-icon-only" @click="updateType"
                                    title="Lưu thay đổi">
                                    <SvgIcon name="save" size="sm" />
                                </button>
                                <button class="btn-action btn-secondary btn-icon-only" @click="editingId = null"
                                    title="Hủy bỏ">
                                    <SvgIcon name="x" size="sm" />
                                </button>
                            </template>
                            <template v-else>
                                <button class="btn-action btn-edit btn-icon-only" @click="startEdit(row)"
                                    :disabled="!canChange" :title="canChange ? 'Chỉnh sửa' : 'Không có quyền sửa'">
                                    <SvgIcon name="edit" size="sm" />
                                </button>
                                <button class="btn-action btn-delete btn-icon-only"
                                    :disabled="row.is_system || !canDelete" @click="confirmDelete(row)"
                                    :title="row.is_system ? 'Không thể xóa loại mặc định' : (canDelete ? 'Xóa loại này' : 'Không có quyền xóa')">
                                    <SvgIcon name="trash" size="sm" />
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
import MasterService from '@/services/master.service';
import auth from '@/store/auth';
import ConfirmModal from '../../components/ConfirmModal.vue';
import SvgIcon from '@/components/common/SvgIcon.vue';
import { errorHandlingMixin } from '../../utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
    name: 'AdminObjectTypes',
    title: 'Quản lý Loại đối tượng',
    components: { SvgIcon, ConfirmModal },
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
        canCreate() { return auth.hasPermission('document_automation.add_masterobjecttype'); },
        canChange() { return auth.hasPermission('document_automation.change_masterobjecttype'); },
        canDelete() { return auth.hasPermission('document_automation.delete_masterobjecttype'); },
    },
    mounted() {
        this.fetchTypes();
    },
    methods: {
        async fetchTypes() {
            try {
                const res = await MasterService.getObjectTypes();
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
                await MasterService.createObjectType(this.newType);
                this.newType = { code: '', name: '', description: '', identity_field_key: '', form_display_mode: null, layout_position: null, dynamic_summary_template: '', order: null };
                this.fetchTypes();
                this.showSuccess('Thêm loại đối tượng thành công!');
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
                await MasterService.updateObjectType(this.editingId, this.editingData);
                this.editingId = null;
                this.fetchTypes();
                this.showSuccess('Cập nhật thành công!');
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
                await MasterService.deleteObjectType(this.deleteTarget.id);
                this.fetchTypes();
                this.showDeleteModal = false;
                this.showSuccess('Xóa loại đối tượng thành công!');
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

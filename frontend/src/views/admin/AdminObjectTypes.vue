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

        <div class="ui-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width: 150px">Mã (Code)</th>
                        <th style="width: 200px">Tên hiển thị</th>
                        <th style="width: 180px">Trường định danh</th>
                        <th style="width: 150px">Phân loại</th>
                        <th style="width: 100px">Vị trí</th>
                        <th style="width: 120px">Cho phép LK</th>
                        <th style="width: 200px">Mẫu hiển thị</th>
                        <th>Mô tả</th>
                        <th style="width: 100px">Hệ thống</th>
                        <th style="width: 70px">Thứ tự</th>
                        <th style="width: 150px">Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="type in types" :key="type.id" :class="{ 'editing-row': editingId === type.id }">
                        <td>
                            <code>{{ type.code }}</code>
                        </td>
                        <td>
                            <input v-if="editingId === type.id" v-model="editingData.name" class="admin-input w-full" />
                            <span v-else class="font-bold">{{ type.name }}</span>
                        </td>
                        <td>
                            <input v-if="editingId === type.id" v-model="editingData.identity_field_key"
                                class="admin-input w-full" />
                            <code v-else>{{ type.identity_field_key || '---' }}</code>
                        </td>
                        <td>
                            <select v-if="editingId === type.id" v-model="editingData.form_display_mode"
                                class="admin-input w-full p-1">
                                <option value="ASSET_LIST">Tài sản</option>
                                <option value="DEDICATED_SECTION">Độc lập</option>
                            </select>
                            <span v-else class="badge"
                                :class="type.form_display_mode === 'DEDICATED_SECTION' ? 'badge-primary' : 'badge-secondary'">
                                {{ getDisplayModeLabel(type.form_display_mode) }}
                            </span>
                        </td>
                        <td>
                            <select v-if="editingId === type.id" v-model="editingData.layout_position"
                                class="admin-input w-full p-1">
                                <option value="LEFT">Trái</option>
                                <option value="RIGHT">Phải</option>
                            </select>
                            <span v-else class="badge"
                                :class="type.layout_position === 'RIGHT' ? 'badge-primary' : 'badge-secondary'">
                                {{ type.layout_position === 'RIGHT' ? '👉 Phải' : '👈 Trái' }}
                            </span>
                        </td>
                        <td>
                            <input v-if="editingId === type.id" v-model="editingData.allow_relations" type="checkbox"
                                class="w-5 h-5" />
                            <span v-else class="badge"
                                :class="type.allow_relations ? 'badge-success' : 'badge-secondary'">
                                {{ type.allow_relations ? '✓ Có' : '✗ Không' }}
                            </span>
                        </td>
                        <td>
                            <input v-if="editingId === type.id" v-model="editingData.dynamic_summary_template"
                                class="admin-input w-full" />
                            <span v-else>{{ type.dynamic_summary_template || '---' }}</span>
                        </td>
                        <td>
                            <input v-if="editingId === type.id" v-model="editingData.description"
                                class="admin-input w-full" />
                            <span v-else>{{ type.description || '---' }}</span>
                        </td>
                        <td>
                            <span v-if="type.is_system" class="badge badge-system">System</span>
                            <span v-else class="badge badge-custom">Custom</span>
                        </td>
                        <td>
                            <input v-if="editingId === type.id" v-model.number="editingData.order" type="number"
                                class="admin-input w-full" style="width: 50px" />
                            <span v-else>{{ type.order }}</span>
                        </td>
                        <td>
                            <div class="flex gap-2">
                                <template v-if="editingId === type.id">
                                    <button class="btn-action btn-save" @click="updateType">Lưu</button>
                                    <button class="btn-action btn-secondary" @click="editingId = null">Hủy</button>
                                </template>
                                <template v-else>
                                    <button class="btn-action btn-edit" @click="startEdit(type)">Sửa</button>
                                    <button class="btn-action btn-delete" :disabled="type.is_system"
                                        @click="confirmDelete(type)"
                                        :title="type.is_system ? 'Không thể xóa loại mặc định' : 'Xóa loại này'">
                                        Xóa
                                    </button>
                                </template>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
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
import ConfirmModal from '../../components/ConfirmModal.vue';
import { makeTableResizable } from '../../utils/resizable-table';
import { errorHandlingMixin } from '../../utils/errorHandler';

export default {
    name: 'AdminObjectTypes',
    components: { ConfirmModal },
    mixins: [errorHandlingMixin],
    data() {
        return {
            types: [],
            newType: { code: '', name: '', description: '', identity_field_key: '', form_display_mode: null, layout_position: null, dynamic_summary_template: '', allow_relations: true, order: null },
            editingId: null,
            editingData: null,
            showDeleteModal: false,
            deleteTarget: null
        };
    },
    mounted() {
        this.fetchTypes();
        this.initResizable();
    },
    methods: {
        async fetchTypes() {
            try {
                const res = await axios.get('http://127.0.0.1:8000/api/object-types/');
                this.types = res.data;
                this.$nextTick(() => this.initResizable());
            } catch (e) {
                this.showError(e, 'Lỗi tải danh sách loại đối tượng');
            }
        },
        initResizable() {
            const table = this.$el.querySelector('.data-table');
            if (table) {
                makeTableResizable(table, 'admin-object-types');
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
                await axios.post('http://127.0.0.1:8000/api/object-types/', this.newType);
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
                await axios.patch(`http://127.0.0.1:8000/api/object-types/${this.editingId}/`, this.editingData);
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
                await axios.delete(`http://127.0.0.1:8000/api/object-types/${this.deleteTarget.id}/`);
                this.fetchTypes();
                this.showDeleteModal = false;
            } catch (e) {
                this.showError(e, 'Lỗi xóa');
            }
        }
    }
};
</script>

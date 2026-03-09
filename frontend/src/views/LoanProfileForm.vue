<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-title">
        <div class="profile-id-badge">#{{ currentId || id || 'NEW' }}</div>
        <label class="profile-name-label">Tên hồ sơ:</label>
        <div class="profile-name-input-wrapper">
          <input v-model="profileName" class="profile-name-input" placeholder="Nhập tên hồ sơ..."
            :disabled="isReadOnly" />
        </div>
        <div v-if="profileStatus" class="status-badge" :class="profileStatus.toLowerCase()">
          {{ $t(profileStatus) }}
        </div>

        <div v-if="currentFormName" class="form-type-badge">
          <span class="badge-label">Mẫu:</span>
          <span class="badge-value">{{ currentFormName }}</span>
        </div>
      </div>
      <div class="header-buttons">
        <button class="btn-action btn-lock btn-icon-only" v-if="profileStatus === 'DRAFT'"
          :disabled="!(id || currentId)" @click="lockProfile" title="Khóa hồ sơ">
          <SvgIcon name="lock" size="sm" />
        </button>
        <button class="btn-action btn-unlock btn-icon-only" v-if="profileStatus === 'FINALIZED'"
          :disabled="!(id || currentId)" @click="unlockProfile" title="Mở khóa hồ sơ">
          <SvgIcon name="unlock" size="sm" />
        </button>

        <button class="btn-action btn-download btn-icon-only" :disabled="!(id || currentId)"
          @click="isDownloadModalOpen = true" title="Xuất Hợp đồng">
          <SvgIcon name="download" size="sm" />
        </button>

        <button class="btn-action btn-secondary btn-history btn-icon-only" :disabled="!(id || currentId)"
          @click="showHistoryDrawer = true" title="Xem lịch sử">
          <SvgIcon name="clock" size="sm" />
        </button>
        <button class="btn-action btn-copy btn-icon-only" :disabled="!(id || currentId)" @click="openDuplicateModal"
          title="Nhân bản hồ sơ">
          <SvgIcon name="copy" size="sm" />
        </button>
        <button class="btn-action btn-save" @click="saveProfile(false)" :disabled="isSaving || isReadOnly"
          :title="isSaving ? 'Đang lưu...' : 'Lưu Hồ Sơ'">
          <SvgIcon v-if="isSaving" name="loading" size="sm" class="spinning" />
          <SvgIcon v-else name="save" size="sm" />
          <span>{{ isSaving ? '...' : 'Lưu' }}</span>
        </button>
      </div>
    </header>

    <div v-if="editingLockedBy" class="lock-banner">
      <div class="lock-content">
        <SvgIcon name="lock" size="sm" />
        <span>Hồ sơ này đang được chỉnh sửa bởi <strong>{{ editingLockedBy }}</strong>. Bạn đang ở chế độ <strong>Chỉ
            xem (Read-only)</strong>.</span>
        <button class="btn-retry" @click="fetchProfileData(currentId || id)">Thử lại</button>
      </div>
    </div>

    <div v-if="loading">Đang tải cấu hình...</div>

    <div v-else class="form-layout" ref="formLayout" @mousemove="onMouseMove" @mouseup="stopResize"
      @mouseleave="stopResize">
      <!-- CỘT TRÁI: THÔNG TIN DỰA TRÊN SEGMENTS -->
      <div class="left-panel" :style="{ width: (showRightPanel ? leftPanelWidth : 100) + '%' }">
        <template v-for="segment in leftPanelSegments" :key="segment.id">
          <!-- Type: GROUP (Thông tin chung - Trường mồ côi) -->
          <div v-if="segment.type === 'GROUP'" class="panel-section orphan-group">
            <h3>{{ segment.name }}</h3>
            <DynamicForm :fields="segment.fields" v-model="generalFieldValues" :disabled="isReadOnly"
              :idPrefix="`gen-l-${segment.id}-`" :allSections="fullProfileData"
              @computed-update="handleComputedUpdate($event)" />
          </div>

          <!-- Type: DEDICATED (Khu vực riêng - VD: Hợp đồng) -->
          <div v-if="segment.type === 'DEDICATED'" class="premium-card theme-dedicated">
            <div class="card-header-glass">
              <div class="header-left">
                <SvgIcon name="shield" size="sm" />
                <h4>{{ segment.name }}</h4>
              </div>
              <div class="header-actions">
                <button class="btn-action btn-secondary btn-sm btn-icon-only" @click="openSelectModal(segment.code)"
                  title="Tìm & Chọn đối tượng">
                  <SvgIcon name="search" size="sm" />
                </button>
                <button class="btn-action btn-secondary btn-sm btn-icon-only" @click="addEntity(segment.code)"
                  title="Thêm mới đối tượng">
                  <SvgIcon name="plus" size="sm" />
                </button>
              </div>
            </div>

            <div class="card-body-content">
              <!-- Trường hợp: Các đối tượng (Asset List/Dedicated List) -->
              <div v-if="!objectSections[segment.code] || objectSections[segment.code].length === 0"
                class="empty-state-standard">
                Chưa có thông tin {{ segment.name }}. Nhấn 'Tìm & Chọn' hoặc 'Thêm mới' để nhập thông tin.
              </div>

              <div v-for="(item, index) in objectSections[segment.code]"
                :key="item.master_object?.id || item._uid || (segment.code + '-' + index)"
                class="premium-card theme-group mt-2">
                <div class="card-header-glass">
                  <div class="header-left">
                    <SvgIcon name="file" size="xs" />
                    <strong>{{ segment.name }} #{{ index + 1 }}</strong>
                  </div>
                  <button class="btn-remove-mini" @click="removeEntity(segment.code, index)">
                    <SvgIcon name="trash" size="sm" />
                  </button>
                </div>
                <div class="card-body-content">
                  <DynamicForm :fields="getFieldsForType(segment.code)" v-model="item.individual_field_values"
                    :disabled="isReadOnly" :idPrefix="`ded-${segment.code.toLowerCase()}-${index}-`"
                    :allSections="fullProfileData"
                    @computed-update="handleComputedUpdate($event, segment.code, index)" />

                  <RelationManager v-if="item.master_object && item.master_object.id"
                    :masterObjectId="item.master_object.id" :profileObjects="allSavedObjects"
                    :currentObjectType="segment.code" :refreshTrigger="relationRefreshTrigger" :allFields="allFields"
                    :disabled="isReadOnly" />
                </div>
              </div>
            </div>
          </div>

          <!-- Type: ASSET_LIST (Danh sách Tài sản) -->
          <div v-else-if="segment.type === 'ASSET_LIST'" class="premium-card theme-asset">
            <div class="card-header-glass">
              <div class="header-left">
                <SvgIcon name="shield" size="sm" />
                <h3>Danh sách Tài sản</h3>
              </div>
              <div class="header-actions">
                <button class="btn-action btn-secondary btn-sm btn-icon-only" @click="addEntity(null)"
                  title="Thêm Tài sản">
                  <SvgIcon name="plus" size="sm" />
                </button>
              </div>
            </div>
            <div class="card-body-content">
              <div v-if="computedAssetList.length === 0" class="empty-state-standard">Chưa có tài sản nào.</div>
              <div v-for="(asset, index) in computedAssetList" :key="asset.master_object?.id || asset._uid">
                <AssetForm :index="index" :asset="asset" :assetFields="getAssetFields()" :availableTypes="objectTypes"
                  :profileObjects="allSavedObjects" :refreshTrigger="relationRefreshTrigger" :allFields="allFields"
                  :allSections="fullProfileData" @update:asset="updateAssetList(index, $event)"
                  @remove="removeAssetList(index)"
                  @computed-update="handleComputedUpdate($event, asset._originalType, asset._originalIdx)" />
              </div>
            </div>
          </div>

          <!-- Type: PERSON_LIST (Danh sách Người liên quan) -->
          <div v-else-if="segment.type === 'PERSON_LIST'" class="premium-card theme-person">
            <div class="card-header-glass">
              <div class="header-left">
                <SvgIcon name="users" size="sm" />
                <h3>Danh sách Người liên quan</h3>
              </div>
              <div class="header-actions">
                <button class="btn-action btn-secondary btn-sm btn-icon-only" @click="addEntity('PERSON')"
                  title="Thêm Người">
                  <SvgIcon name="plus" size="sm" />
                </button>
              </div>
            </div>
            <div class="card-body-content">
              <div v-if="!objectSections['PERSON'] || objectSections['PERSON'].length === 0"
                class="empty-state-standard">
                Chưa có người nào liên quan.
              </div>
              <div v-for="(person, index) in objectSections['PERSON']" :key="person.master_object?.id || person._uid">
                <PersonForm :index="index" :person="person" :personFields="getFieldsForType('PERSON')"
                  :availableRoles="availableRoles" :availableTypes="objectTypes" :profileObjects="allSavedObjects"
                  :refreshTrigger="relationRefreshTrigger" :allFields="allFields" :allSections="fullProfileData"
                  @update:person="updateEntity('PERSON', index, $event)" @remove="removeEntity('PERSON', index)"
                  @computed-update="handleComputedUpdate($event, 'PERSON', index)" />
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- THANH KÉO (DRAG HANDLE) -->
      <div class="resize-handle" @mousedown="startResize" v-if="showRightPanel">
        <div class="handle-icon">||</div>
      </div>

      <!-- CỘT PHẢI: THÔNG TIN DỰA TRÊN SEGMENTS -->
      <div class="right-panel" :style="{ width: (100 - leftPanelWidth) + '%' }" v-if="showRightPanel">
        <template v-for="segment in rightPanelSegments" :key="segment.id">
          <!-- Type: GROUP (Thông tin chung - Trường mồ côi) -->
          <div v-if="segment.type === 'GROUP'" class="panel-section orphan-group">
            <h3>{{ segment.name }}</h3>
            <DynamicForm :fields="segment.fields" v-model="generalFieldValues" :disabled="isReadOnly"
              :idPrefix="`gen-r-${segment.id}-`" :allSections="fullProfileData"
              @computed-update="handleComputedUpdate($event)" />
          </div>

          <!-- Type: DEDICATED (Khu vực riêng - VD: Hợp đồng) -->
          <div v-if="segment.type === 'DEDICATED'" class="premium-card theme-dedicated">
            <div class="card-header-glass">
              <div class="header-left">
                <SvgIcon name="shield" size="sm" />
                <h4>{{ segment.name }}</h4>
              </div>
              <div class="header-actions">
                <button class="btn-action btn-secondary btn-sm btn-icon-only" @click="openSelectModal(segment.code)"
                  title="Tìm & Chọn đối tượng">
                  <SvgIcon name="search" size="sm" />
                </button>
                <button class="btn-action btn-secondary btn-sm btn-icon-only" @click="addEntity(segment.code)"
                  title="Thêm mới đối tượng">
                  <SvgIcon name="plus" size="sm" />
                </button>
              </div>
            </div>

            <div class="card-body-content">
              <!-- Trường hợp: Các đối tượng -->
              <div v-if="!objectSections[segment.code] || objectSections[segment.code].length === 0"
                class="empty-state-standard">
                Chưa có thông tin {{ segment.name }}. Nhấn 'Tìm & Chọn' hoặc 'Thêm mới' để nhập thông tin.
              </div>

              <div v-for="(item, index) in objectSections[segment.code]"
                :key="item.master_object?.id || item._uid || (segment.code + '-' + index)"
                class="premium-card theme-group mt-2">
                <div class="card-header-glass">
                  <div class="header-left">
                    <SvgIcon name="file" size="xs" />
                    <strong>{{ segment.name }} #{{ index + 1 }}</strong>
                  </div>
                  <button class="btn-remove-mini" @click="removeEntity(segment.code, index)">
                    <SvgIcon name="trash" size="sm" />
                  </button>
                </div>
                <div class="card-body-content">
                  <DynamicForm :fields="getFieldsForType(segment.code)" v-model="item.individual_field_values"
                    :disabled="isReadOnly" :idPrefix="`ded-${segment.code.toLowerCase()}-${index}-`"
                    :allSections="fullProfileData"
                    @computed-update="handleComputedUpdate($event, segment.code, index)" />

                  <RelationManager v-if="item.master_object && item.master_object.id"
                    :masterObjectId="item.master_object.id" :profileObjects="allSavedObjects"
                    :currentObjectType="segment.code" :refreshTrigger="relationRefreshTrigger" :allFields="allFields"
                    :disabled="isReadOnly" />
                </div>
              </div>
            </div>
          </div>

          <!-- Type: ASSET_LIST (Danh sách Tài sản) -->
          <div v-else-if="segment.type === 'ASSET_LIST'" class="premium-card theme-asset">
            <div class="card-header-glass">
              <div class="header-left">
                <SvgIcon name="shield" size="sm" />
                <h3>Danh sách Tài sản</h3>
              </div>
              <div class="header-actions">
                <button class="btn-action btn-secondary btn-sm btn-icon-only" @click="addEntity(null)"
                  title="Thêm Tài sản">
                  <SvgIcon name="plus" size="sm" />
                </button>
              </div>
            </div>
            <div class="card-body-content">
              <div v-if="computedAssetList.length === 0" class="empty-state-standard">Chưa có tài sản nào.</div>
              <div v-for="(asset, index) in computedAssetList" :key="asset.master_object?.id || asset._uid">
                <AssetForm :index="index" :asset="asset" :assetFields="getAssetFields()" :availableTypes="objectTypes"
                  :profileObjects="allSavedObjects" :refreshTrigger="relationRefreshTrigger" :allFields="allFields"
                  :allSections="fullProfileData" @update:asset="updateAssetList(index, $event)"
                  @remove="removeAssetList(index)"
                  @computed-update="handleComputedUpdate($event, asset._originalType, asset._originalIdx)" />
              </div>
            </div>
          </div>

          <!-- Type: PERSON_LIST (Danh sách Người liên quan) -->
          <div v-else-if="segment.type === 'PERSON_LIST'" class="premium-card theme-person">
            <div class="card-header-glass">
              <div class="header-left">
                <SvgIcon name="users" size="sm" />
                <h3>Danh sách Người liên quan</h3>
              </div>
              <button class="btn-action btn-secondary btn-sm" @click="addEntity('PERSON')">
                <SvgIcon name="plus" size="xs" />
                <span>Thêm Người</span>
              </button>
            </div>
            <div class="card-body-content">
              <div v-if="!objectSections['PERSON'] || objectSections['PERSON'].length === 0"
                class="empty-state-standard">
                Chưa có người nào liên quan.
              </div>
              <div v-for="(person, index) in objectSections['PERSON']" :key="person.master_object?.id || person._uid">
                <PersonForm :index="index" :person="person" :personFields="getFieldsForType('PERSON')"
                  :availableRoles="availableRoles" :availableTypes="objectTypes" :profileObjects="allSavedObjects"
                  :refreshTrigger="relationRefreshTrigger" :allFields="allFields" :allSections="fullProfileData"
                  @update:person="updateEntity('PERSON', index, $event)" @remove="removeEntity('PERSON', index)"
                  @computed-update="handleComputedUpdate($event, 'PERSON', index)" />
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal :visible="showDeleteModal" :title="deleteModalTitle" :message="deleteModalMessage" confirmText="Xóa"
      @confirm="confirmDelete" @cancel="showDeleteModal = false" />

    <!-- Duplicate Modal -->
    <InputModal :visible="showDuplicateModal" title="Tạo bản sao hồ sơ" label="Tên hồ sơ mới:"
      :defaultValue="duplicateDefaultName" confirmText="Tạo bản sao" @confirm="confirmDuplicate"
      @cancel="showDuplicateModal = false" />

    <!-- Lock Password Modal -->
    <InputModal :visible="showLockPasswordModal" title="Khóa hồ sơ" label="Thiết lập mật khẩu để khóa hồ sơ:"
      confirmText="Khóa" @confirm="handleLockPassword" @cancel="showLockPasswordModal = false" />

    <!-- Unlock Password Modal -->
    <InputModal :visible="showUnlockPasswordModal" title="Mở khóa hồ sơ" label="Nhập mật khẩu để mở khóa:"
      confirmText="Mở khóa" @confirm="handleUnlockPassword" @cancel="showUnlockPasswordModal = false" />

    <!-- Error Modal (from mixin) -->
    <ConfirmModal :visible="showErrorModal" type="error" mode="alert" :title="errorModalTitle"
      :message="errorModalMessage" :errorCode="errorModalCode" :details="errorModalDetails" :showTimestamp="true"
      confirmText="Đóng" @confirm="showErrorModal = false" @cancel="showErrorModal = false" />

    <!-- Success Modal (from mixin) -->
    <ConfirmModal :visible="showSuccessModal" type="success" mode="alert" :title="successModalTitle"
      :message="successModalMessage" confirmText="OK" @confirm="showSuccessModal = false"
      @cancel="showSuccessModal = false" />

    <!-- Warning Modal (from mixin) -->
    <ConfirmModal :visible="showWarningModal" type="warning" mode="alert" :title="warningModalTitle"
      :message="warningModalMessage" confirmText="Đóng" @confirm="showWarningModal = false"
      @cancel="showWarningModal = false" />

    <!-- Contract Downloader Modal -->
    <ContractDownloader :isOpen="isDownloadModalOpen" :profileId="Number(currentId || id)" :profileName="profileName"
      @close="isDownloadModalOpen = false" />

    <ObjectSelectModal :isOpen="showUniversalSelect" :type="currentSelectType" @select="handleUniversalSelect"
      @close="showUniversalSelect = false" />

    <!-- MANDATORY DUPLICATE CONFIRMATION MODAL -->
    <ConfirmModal :visible="showDuplicateConfirmModal" type="warning" mode="confirm"
      title="Cảnh báo trùng lặp định danh" message="" confirmText="Vẫn lưu - Tôi hiểu rõ"
      cancelText="Hủy - Quay lại chỉnh sửa" @confirm="performSaveProfile(pendingSaveSilent)"
      @cancel="showDuplicateConfirmModal = false">
      <template #default>
        <div class="duplicate-confirm-content">
          <div class="info-box warning">
            <div class="info-box-icon">
              <SvgIcon name="alert" size="sm" />
            </div>
            <div class="info-box-content">
              <strong>Bạn đang lưu thông tin định danh (CCCD/Mã định danh) trùng với dữ liệu gốc đã tồn tại:</strong>
            </div>
          </div>

          <table class="duplicate-comparison-table data-table">
            <thead>
              <tr>
                <th>Loại đối tượng</th>
                <th>Thông tin bạn vừa nhập</th>
                <th>Dữ liệu hiện có (Master Data)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in duplicateConfirmList" :key="idx">
                <td>{{ item.type }}</td>
                <td class="current-input">{{ item.value }}</td>
                <td class="master-data">
                  <div class="master-name">{{ item.name }}</div>
                  <div class="master-id">ID: #{{ item.master_object?._duplicateMasterId }}</div>
                </td>
              </tr>
            </tbody>
          </table>

          <div class="info-box info">
            <div class="info-box-icon">
              <SvgIcon name="info" size="sm" />
            </div>
            <div class="info-box-content">
              <span class="info-box-title">💡 Giải thích về tính năng Bảo toàn dữ liệu (Snapshot):</span>
              <div class="mb-2">
                <strong>Dữ liệu này là Bản chụp (Snapshot):</strong>
                Hệ thống sẽ lưu chính xác thông tin bạn vừa nhập <strong>chỉ dành riêng cho hồ sơ này</strong> để phục
                vụ in ấn và pháp lý tại thời điểm hiện tại.
              </div>
              <div class="mb-2">
                <strong>KHÔNG ghi đè Dữ liệu Gốc:</strong>
                Hành động này <strong>KHÔNG</strong> cập nhật hay làm thay đổi thông tin trong danh mục Dữ liệu Gốc
                (Master Data).
              </div>
              <div>
                <strong>Cách sửa Dữ liệu Gốc:</strong>
                Nếu bạn muốn thay đổi thông tin chính thức của đối tượng này cho toàn hệ thống, vui lòng truy cập menu
                <strong>Quản lý → Dữ liệu Gốc</strong>.
              </div>
            </div>
          </div>
        </div>
      </template>
    </ConfirmModal>

    <!-- CONTRACT DOWNLOADER MODAL -->
    <ContractDownloader :isOpen="isDownloadModalOpen" :profileId="Number(id || currentId)" :profileName="profileName"
      @close="isDownloadModalOpen = false" />

    <!-- HISTORY DRAWER (Slide-over) -->
    <Teleport to="body">
      <div class="drawer-overlay" v-if="showHistoryDrawer" @click="showHistoryDrawer = false"></div>
      <div class="drawer-panel" :class="{ 'is-open': showHistoryDrawer }">
        <div class="drawer-header">
          <h3>Nhật ký Hồ sơ</h3>
          <button class="btn-close-drawer" @click="showHistoryDrawer = false">&times;</button>
        </div>
        <div class="drawer-body">
          <HistoryTimeline v-if="showHistoryDrawer" :apiUrl="historyApiUrl" />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import DynamicForm from '../components/DynamicForm.vue';
import PersonForm from '../components/PersonForm.vue';
import AssetForm from '../components/AssetForm.vue';
import ConfirmModal from '../components/ConfirmModal.vue';
import InputModal from '../components/InputModal.vue';
import ContractDownloader from '../components/ContractDownloader.vue';
import ObjectSelectModal from '../components/ObjectSelectModal.vue';
import RelationManager from '../components/RelationManager.vue';
import HistoryTimeline from '../components/HistoryTimeline.vue';
import SvgIcon from '../components/common/SvgIcon.vue';
import { errorHandlingMixin } from '../utils/errorHandler';

export default {
  name: 'LoanProfileForm',
  components: {
    DynamicForm, PersonForm, AssetForm, ConfirmModal,
    InputModal, ContractDownloader, ObjectSelectModal,
    RelationManager, HistoryTimeline, SvgIcon
  },
  mixins: [errorHandlingMixin],
  props: ['id'],
  data() {
    return {
      loading: true,
      isSaving: false,
      allFields: [],
      profileName: '',
      generalFieldValues: {},
      objectSections: {}, // MỚI: Dùng thay cho people, assets, attorneys
      currentId: null,
      availableRoles: [],
      currentFormSlug: null, // MỚI: Theo dõi slug form hiện tại
      currentFormName: '', // MỚI: Tên hiển thị của form
      objectTypes: [], // List of MasterObjectTypes for AssetForm filtering
      autoSaveInterval: null, // MỚI: Bộ đếm thời gian tự động lưu
      suppressComputedUpdate: false, // Cờ chặn computed-update khi reload dữ liệu
      // Resize logic
      leftPanelWidth: 50,
      isResizing: false,
      collapsedSections: {},
      // Confirm Modal State
      showDeleteModal: false,
      deleteModalTitle: '',
      deleteModalMessage: '',
      deleteAction: null,
      deleteIndex: null,
      // Download Modal
      isDownloadModalOpen: false,

      // Duplicate Modal
      showDuplicateConfirmModal: false,
      duplicateConfirmList: [],
      lastConfirmedDuplicateValues: {}, // Key: _uid, Value: identifier value
      pendingSaveSilent: false,
      showDuplicateModal: false,
      duplicateDefaultName: '',

      // Password Input Modals
      showLockPasswordModal: false,
      showUnlockPasswordModal: false,
      relationRefreshTrigger: 0,

      // Auto-save timer
      autoSaveTimer: null,
      // Profile Status
      profileStatus: 'DRAFT',

      // UOS Universal Selection
      showUniversalSelect: false,
      currentSelectType: 'PERSON',

      // History Drawer
      showHistoryDrawer: false,

      // Locking
      editingLockedBy: null,
      heartbeatInterval: null,
    };
  },
  computed: {
    isReadOnly() {
      return this.profileStatus === 'FINALIZED' || !!this.editingLockedBy;
    },
    historyApiUrl() {
      const pid = this.currentId || this.id;
      const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';
      return pid ? `${API_URL}/loan-profiles/${pid}/history/` : '';
    },
    getSegmentsByPosition() {
      return (position) => {
        let segments = [];

        // 1. Nhóm các Trường mồ côi (Field Groups not linked to Object Types)
        const groups = this.allFields.reduce((acc, field) => {
          const gSlug = field.group_slug || 'other';
          const gPos = field.group_layout_position || 'LEFT';
          if (gPos !== position) return acc;

          // Chỉ lấy các trường "Mồ côi" (không gắn với Object Type nào qua Nhóm)
          const specialTypes = field.group_allowed_object_type_codes || [];
          if (specialTypes.length > 0) return acc;

          if (!acc[gSlug]) {
            acc[gSlug] = {
              id: `group-${gSlug}`,
              type: 'GROUP',
              name: field.group_name || 'Thông tin chung',
              order: field.group_order || 0,
              fields: []
            };
          }
          acc[gSlug].fields.push(field);
          return acc;
        }, {});
        segments.push(...Object.values(groups));

        // 2. Các Dedicated Sections (Bao gồm cả Hồ sơ Gốc)
        const dedicated = this.objectTypes.filter(t =>
          t.form_display_mode === 'DEDICATED_SECTION' &&
          t.code !== 'PERSON' &&
          (t.layout_position || 'LEFT') === position &&
          this.getFieldsForType(t.code).length > 0
        ).map(t => ({
          id: `dedicated-${t.code}`,
          type: 'DEDICATED',
          name: t.name,
          order: t.order || 0,
          code: t.code
        }));
        segments.push(...dedicated);

        // 3. Danh sách Tài sản (Asset List)
        // Tìm cấu hình Asset List (mặc định LEFT nếu không tìm thấy field nào setup)
        const hasAssetFields = this.assetListTypes.length > 0;
        if (hasAssetFields) {
          const assetFields = this.getAssetFields();
          const assetPos = assetFields.length > 0 ? (assetFields[0].group_layout_position || 'LEFT') : 'LEFT';
          if (assetPos === position) {
            // Lấy order từ loại đối tượng đầu tiên trong asset list types (hoặc config riêng nếu có)
            // Ở đây ta dùng cái đầu tiên làm đại diện cho cả "Danh sách tài sản"
            const firstType = this.objectTypes.find(t => this.assetListTypes.includes(t.code));
            segments.push({
              id: 'asset-list',
              type: 'ASSET_LIST',
              name: 'Danh sách Tài sản',
              order: firstType ? (firstType.order || 0) : 0
            });
          }
        }

        // 4. Danh sách Người (PERSON)
        const personFields = this.getFieldsForType('PERSON');
        if (personFields.length > 0) {
          const personType = this.objectTypes.find(t => t.code === 'PERSON');
          const personPos = personType ? (personType.layout_position || 'LEFT') : 'LEFT';
          if (personPos === position) {
            segments.push({
              id: 'person-list',
              type: 'PERSON_LIST',
              name: 'Danh sách Người liên quan',
              order: personType ? (personType.order || 0) : 0
            });
          }
        }

        return segments.sort((a, b) => a.order - b.order);
      };
    },
    leftPanelSegments() {
      return this.getSegmentsByPosition('LEFT');
    },
    rightPanelSegments() {
      return this.getSegmentsByPosition('RIGHT');
    },
    // Keep legacy computed for backward compatibility if needed, but we will use segments
    leftPanelGroups() { return {}; },
    rightPanelGroups() { return {}; },
    isAssetRight() { return false; },
    isPersonRight() { return false; },
    // Danh sách tất cả các đối tượng đã lưu (có ID) trong hồ sơ hiện tại
    allSavedObjects() {
      const list = [];
      Object.keys(this.objectSections).forEach(typeCode => {
        this.objectSections[typeCode].forEach(item => {
          if (item.master_object && item.master_object.id) {
            const typeConfig = this.objectTypes.find(t => t.code === typeCode);
            const typeName = typeConfig ? typeConfig.name : typeCode;

            let displayName = '';
            const fv = item.individual_field_values || {};

            if (typeConfig && typeConfig.identity_field_key) {
              displayName = fv[typeConfig.identity_field_key];
            }

            if (!displayName) {
              // Fallback labels
              displayName = fv.ho_ten ||
                fv.ten_tai_san ||
                fv.so_dien_thoai ||
                fv.bien_so_xe ||
                fv.chung_nhan_qsdd ||
                `#${item.master_object.id}`;
            }

            list.push({
              id: item.master_object.id,
              object_type: typeName,
              origin_type_code: typeCode,
              allow_relations: typeConfig ? (typeConfig.allow_relations !== false) : true,
              display_name: `[${this.$t(typeName)}] ${displayName}`
            });
          }
        });
      });
      return list;
    },
    // --- UOS COMPUTED ---
    dedicatedSections() {
      // Lấy danh sách các loại đối tượng có mode DEDICATED_SECTION
      return this.objectTypes.filter(t => t.form_display_mode === 'DEDICATED_SECTION');
    },
    assetListTypes() {
      // Lấy mã của các loại đối tượng gom trong danh sách Tài sản
      return this.objectTypes
        .filter(t => t.form_display_mode === 'ASSET_LIST' && t.code !== 'PERSON')
        .map(t => t.code);
    },
    getFieldsForType() {
      return (typeCode) => {
        return this.allFields.filter(f => {
          const groupAllowed = f.group_allowed_object_type_codes || [];
          const fieldAllowed = f.allowed_object_type_codes || [];

          // Logic ưu tiên:
          // 1. Nếu FIELD có định nghĩa loại cụ thể -> Chỉ theo FIELD
          if (fieldAllowed.length > 0) {
            return fieldAllowed.includes(typeCode);
          }

          // 2. Nếu FIELD không có nhưng GROUP có -> Theo GROUP
          if (groupAllowed.length > 0) {
            return groupAllowed.includes(typeCode);
          }

          // 3. Nếu cả hai đều trống -> Cho phép tất cả (tố cốt lõi của hồ sơ)
          return true;
        });
      }
    },
    showRightPanel() {
      return this.rightPanelSegments.length > 0;
    },
    coreFields() {
      // Thông tin CỐT LÕI (CORE) = Các trường không thuộc bất kỳ object_type nào (General Profile)
      return this.allFields.filter(f => {
        const specialTypes = f.group_allowed_object_type_codes || [];
        return specialTypes.length === 0;
      }).sort((a, b) => a.order - b.order);
    },
    // Dữ liệu hợp nhất toàn bộ hồ sơ để phục vụ tính toán công thức (Computed Fields)
    fullProfileData() {
      return {
        ...this.objectSections,
        _GENERAL_: this.generalFieldValues
      };
    },
    // Danh sách tài sản gộp từ tất cả objectSections (cached, không tạo object mới mỗi lần render)
    computedAssetList() {
      const list = [];
      const seenTypes = new Set();

      // Collect all assets from all relevant sections
      this.assetListTypes.forEach(t => {
        seenTypes.add(t);
        if (this.objectSections[t]) {
          this.objectSections[t].forEach((item, idx) => {
            list.push({ ...item, _originalType: t, _originalIdx: idx });
          });
        }
      });

      if (this.objectSections['ASSET']) {
        this.objectSections['ASSET'].forEach((item, idx) => {
          list.push({ ...item, _originalType: 'ASSET', _originalIdx: idx });
        });
      }

      // Sắp xếp theo _uid giảm dần (Mới nhất lên đầu)
      return list.sort((a, b) => {
        const valA = a._uid || a.master_object?.id || 0;
        const valB = b._uid || b.master_object?.id || 0;
        return valB - valA;
      });
    }
  },
  async mounted() {
    await this.fetchFields();
    this.fetchRoles();
    await this.fetchObjectTypes();
    if (this.id) {
      this.currentId = this.id;
      await this.fetchProfileData(this.id);
    }
    // Thiết lập Auto-save định kỳ 2 phút (120000ms)
    this.autoSaveInterval = setInterval(() => {
      if (this.currentId || this.id) {
        this.saveProfile(true); // silent = true
      }
    }, 120000);
    // ĐÃ XÓA: Tự động addEntity('PERSON') và addEntity(null) để tránh tạo rác
  },
  watch: {
    // Watchers for other logic if needed in future
    id: {
      handler(newId) {
        if (newId) {
          this.currentId = newId;
          this.fetchProfileData(newId);
        } else {
          // Reset data for new profile
          this.currentId = null;
          this.profileName = '';
          this.profileStatus = 'DRAFT';
          this.generalFieldValues = {};
          this.objectSections = {};
          this.applyDefaultsToGeneral();
        }
      }
    },
    '$route.query.form': {
      handler() {
        this.fetchFields();
      }
    }
  },
  beforeUnmount() {
    // Dọn dẹp bộ đếm khi thoát trang
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }
    window.removeEventListener('beforeunload', this.onBeforeUnload);
    this.stopHeartbeat();
    this.releaseLock();
  },
  methods: {
    // Nhận kết quả tính toán từ DynamicForm computed fields → cập nhật vào đúng ngữ cảnh
    handleComputedUpdate(computedVals, typeCode = null, index = null) {
      // Guard: Không xử lý khi đang reload dữ liệu từ server
      if (this.suppressComputedUpdate) return;
      if (!computedVals || Object.keys(computedVals).length === 0) return;

      let hasChange = false;

      if (typeCode && index !== null) {
        // Cập nhật cụ thể cho một đối tượng trong objectSections
        if (!this.objectSections[typeCode] || !this.objectSections[typeCode][index]) return;

        const item = this.objectSections[typeCode][index];
        const currentFv = { ...item.individual_field_values };

        Object.keys(computedVals).forEach(key => {
          const newVal = computedVals[key];
          // Kiểm tra giá trị thực sự khác biệt để tránh loop
          if (newVal !== undefined && newVal !== null && currentFv[key] !== newVal) {
            currentFv[key] = newVal;
            hasChange = true;
          }
        });

        if (hasChange) {
          item.individual_field_values = currentFv;
          // Trigger reactivity cho objectSections bằng cách clone nông
          this.objectSections = { ...this.objectSections };
        }
      } else {
        // Cập nhật cho các trường thông tin chung (General)
        const currentValues = { ...this.generalFieldValues };
        Object.keys(computedVals).forEach(key => {
          const newVal = computedVals[key];
          if (newVal !== undefined && newVal !== null && currentValues[key] !== newVal) {
            currentValues[key] = newVal;
            hasChange = true;
          }
        });

        if (hasChange) {
          this.generalFieldValues = currentValues;
        }
      }
    },
    toggleSection(key) {
      // Toggle trạng thái: Nếu chưa có thì set true (collapsed), có rồi thì đảo ngược
      this.collapsedSections[key] = !this.collapsedSections[key];
    },
    isCollapsed(key) {
      return !!this.collapsedSections[key];
    },
    startResize() { this.isResizing = true; },
    stopResize() { this.isResizing = false; },
    onMouseMove(e) {
      if (!this.isResizing) return;
      const container = this.$refs.formLayout;
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const offsetX = e.clientX - rect.left;
      const newWidthPercent = (offsetX / rect.width) * 100;
      if (newWidthPercent > 20 && newWidthPercent < 80) {
        this.leftPanelWidth = newWidthPercent;
      }
    },
    async fetchObjectTypes() {
      try {
        const res = await axios.get(`${API_URL}/object-types/`);
        this.objectTypes = res.data;
      } catch (e) { console.error("Lỗi load object types:", e); }
    },
    async fetchRoles() {
      try {
        const res = await axios.get(`${API_URL}/roles/`);
        this.availableRoles = res.data.map(r => r.name);
      } catch (e) { console.error("Lỗi load roles:", e); }
    },
    async fetchFields() {
      const form_slug = this.$route.query.form || this.currentFormSlug || "";
      try {
        const url = `${API_URL}/fields/?form_slug=${form_slug}`;
        const response = await axios.get(url);
        this.allFields = response.data;

        // Luôn kiểm tra và áp dụng giá trị mặc định cho các trường chung còn trống
        this.applyDefaultsToGeneral();

        // MỞ RỘNG: Áp dụng giá trị mặc định cho tất cả các đối tượng trong objectSections
        Object.keys(this.objectSections).forEach(typeCode => {
          const fields = this.getFieldsForType(typeCode);
          const defaults = this.getDefaultValuesFor(fields);
          this.objectSections[typeCode].forEach(item => {
            const currentValues = item.individual_field_values || {};
            let changed = false;
            Object.keys(defaults).forEach(key => {
              // Áp dụng nếu key chưa tồn tại hoặc rỗng/null
              if (currentValues[key] === undefined || currentValues[key] === null || currentValues[key] === '') {
                currentValues[key] = defaults[key];
                changed = true;
              }
            });
            if (changed) {
              item.individual_field_values = { ...currentValues };
            }
          });
        });
      } catch (e) {
        console.error(e);
        this.showError(e, 'Lỗi tải cấu hình fields');
      } finally {
        this.loading = false;
        this.fetchFormDetails(form_slug);
      }
    },
    async fetchFormDetails(slug) {
      if (!slug) {
        this.currentFormName = '';
        return;
      }
      try {
        const res = await axios.get(`${API_URL}/form-views/`);
        const target = res.data.find(f => f.slug === slug);
        if (target) {
          this.currentFormName = target.name;
        }
      } catch (e) {
        console.error("Lỗi load chi tiết form:", e);
      }
    },
    applyDefaultsToGeneral() {
      // Áp dụng giá trị mặc định cho tất cả các trường CHUNG hiển thị trong Panel
      // Logic MATCH với getGroupsByPosition để đảm bảo nhất quán
      const currentValues = { ...this.generalFieldValues };
      this.allFields.forEach(field => {
        const specialTypes = field.group_allowed_object_type_codes || [];
        if (specialTypes.length === 0) {
          if (field.default_value && (currentValues[field.placeholder_key] === undefined || currentValues[field.placeholder_key] === null || currentValues[field.placeholder_key] === '')) {
            currentValues[field.placeholder_key] = field.default_value;
          }
        }
      });
      this.generalFieldValues = currentValues;
    },
    getDefaultValuesFor(fieldsArray) {
      // Tạo object chứa giá trị mặc định cho một mảng fields
      const defaults = {};
      fieldsArray.forEach(field => {
        if (field.default_value) {
          defaults[field.placeholder_key] = field.default_value;
        }
      });
      return defaults;
    },
    // --- GENERIC ENTITY ACTIONS ---
    updateEntity(typeCode, index, updated) {
      if (!this.objectSections[typeCode]) return;

      const oldType = typeCode;
      const newType = updated.master_object?.object_type;

      // Làm mới _uid khi đổi loại để đưa lên đầu danh sách toàn cục
      if (newType && newType !== oldType) {
        updated._uid = Date.now() + Math.random();
        console.log(`DEBUG: Di chuyển đối tượng từ ${oldType} sang ${newType} và làm mới _uid`);

        // 1. Xóa khỏi mảng cũ
        this.objectSections[oldType].splice(index, 1);

        // 2. Thêm vào mảng mới
        if (!this.objectSections[newType]) {
          this.objectSections[newType] = [];
        }
        // Đưa lên đầu mảng mới
        this.objectSections[newType].unshift(updated);

        this.$toast.info(`Đã chuyển loại sang: ${this.$t(newType)}`);

      } else {
        // Cập nhật giá trị bình thường trong cùng một mảng
        this.objectSections[typeCode][index] = updated;
      }
    },
    async addEntity(typeCode) {
      let targetType = typeCode;

      // Nếu không có typeCode -> Cho vào ngăn chứa chung 'ASSET' nhưng object_type = null để bắt buộc người dùng chọn
      if (!targetType) {
        targetType = 'ASSET';
      }

      const fields = this.getFieldsForType(targetType);
      const defaults = this.getDefaultValuesFor(fields);

      if (!this.objectSections[targetType]) {
        this.objectSections[targetType] = [];
      }

      this.objectSections[targetType].unshift({
        _uid: Date.now() + Math.random(),
        id: null,
        master_object: { object_type: typeCode }, // Có thể là null nếu typeCode=null
        individual_field_values: { ...defaults },
        roles: targetType === 'ATTORNEY' ? ['đại diện'] : []
      });

      // Auto-save đã bị loại bỏ theo yêu cầu: avoid saving empty entities
      // if (this.currentId) { await this.saveProfile(); }

      // Trigger generic refresh for relations
      this.relationRefreshTrigger++;
    },
    removeEntity(typeCode, index) {
      const item = this.objectSections[typeCode][index];
      const typeCfg = this.objectTypes.find(t => t.code === typeCode);
      const name = item.individual_field_values?.ho_ten ||
        item.individual_field_values?.nguoi_dai_dien ||
        `${typeCfg?.name || typeCode} #${index + 1}`;

      this.deleteModalTitle = 'Xác nhận xóa';
      this.deleteModalMessage = `Bạn có chắc muốn xóa '${name}' khỏi hồ sơ?`;
      this.deleteAction = 'uos_entity';
      this.deleteContext = { typeCode, index };
      this.showDeleteModal = true;
    },
    confirmDelete() {
      if (this.deleteAction === 'uos_entity') {
        const { typeCode, index } = this.deleteContext;
        if (this.objectSections[typeCode]) {
          this.objectSections[typeCode].splice(index, 1);
          this.$toast.success('Đã xóa đối tượng');
        }
      }
      this.showDeleteModal = false;
    },

    // --- ASSET LIST COMPATIBILITY ---
    // getAssetList() đã được chuyển thành computed property: computedAssetList
    getAssetFields() {
      // Lấy tất cả các fields thuộc về bất kỳ loại tài sản nào trong assetListTypes
      return this.allFields.filter(f => {
        const groupAllowed = f.group_allowed_object_type_codes || [];
        const fieldAllowed = f.allowed_object_type_codes || [];

        // Logic ưu tiên cho Asset Fields:
        // Nếu có FIELD cụ thể, kiểm tra xem nó có thuộc bất kỳ loại tài sản nào không
        if (fieldAllowed.length > 0) {
          return fieldAllowed.some(t => this.assetListTypes.includes(t));
        }

        // Nếu không có FIELD nhưng có GROUP, kiểm tra GROUP
        if (groupAllowed.length > 0) {
          return groupAllowed.some(t => this.assetListTypes.includes(t));
        }

        // Nếu cả hai đều trống -> Đây là general field, không phải asset field chuyên dụng
        return false;
      });
    },
    updateAssetList(index, updated) {
      const list = this.computedAssetList;
      const target = list[index];
      if (target) {
        this.updateEntity(target._originalType, target._originalIdx, updated);
      }
    },
    removeAssetList(index) {
      const list = this.computedAssetList;
      const target = list[index];
      if (target) {
        this.removeEntity(target._originalType, target._originalIdx);
      }
    },

    openSelectModal(typeCode) {
      this.currentSelectType = typeCode;
      this.showUniversalSelect = true;
    },
    handleUniversalSelect(masterObj) {
      const tCode = masterObj.object_type;
      if (!this.objectSections[tCode] || this.objectSections[tCode].length === 0) {
        this.addEntity(tCode);
      }
      const lastIdx = this.objectSections[tCode].length - 1;
      this.handleSelectEntity(tCode, lastIdx, masterObj);
    },
    handleSelectEntity(typeCode, index, masterObj) {
      if (!this.objectSections[typeCode]) return;
      const item = this.objectSections[typeCode][index];

      // Làm mới _uid để đưa mục vừa chọn lên đầu danh sách (UX)
      item._uid = Date.now() + Math.random();

      item.id = masterObj.id;
      item.master_object = { id: masterObj.id, object_type: typeCode };

      const currentValues = item.individual_field_values || {};
      if (masterObj.field_values) {
        item.individual_field_values = {
          ...currentValues,
          ...masterObj.field_values
        };
      }
      this.$toast.success(`Đã chọn: ${masterObj.display_name}`);
    },

    // Duplicate Actions
    openDuplicateModal() {
      this.duplicateDefaultName = `${this.profileName} - copy`;
      this.showDuplicateModal = true;
    },
    async confirmDuplicate(newName) {
      try {
        const response = await axios.post(
          `${API_URL}/loan-profiles/${this.id}/duplicate/`,
          { new_name: newName }
        );
        this.showDuplicateModal = false;
        this.$toast.success(`Đã tạo bản sao: ${response.data.name}`);
        // Chuyển hướng sang hồ sơ mới
        this.$router.push(`/edit/${response.data.id}`);
        // Vì Vue reuse component khi route thay đổi id, ta cần load lại data
        this.fetchProfileData(response.data.id);
      } catch (error) {
        this.showDuplicateModal = false;
        this.showError(error, 'Lỗi khi tạo bản sao');
      }
    },

    async fetchProfileData(id) {
      try {
        this.loading = true;
        const response = await axios.get(`${API_URL}/loan-profiles/${id}/`);
        const data = response.data;
        this.profileName = data.name || '';
        this.profileStatus = data.status || 'DRAFT';

        // 3. Acquire Lock (New Phase 3)
        await this.acquireLock();

        // Chặn computed-update khi gán dữ liệu mới từ server
        this.suppressComputedUpdate = true;
        this.generalFieldValues = data.field_values || {};

        // MỚI: Load object_sections thay vì people/assets
        const sections = data.object_sections || {};
        // Gán _uid cho các đối tượng cũ để có thể sắp xếp ổn định trong session
        Object.keys(sections).forEach(type => {
          sections[type].forEach(item => {
            if (!item._uid) item._uid = item.master_object?.id || 0;
          });
        });
        this.objectSections = sections;
        this.$nextTick(() => { this.suppressComputedUpdate = false; });

        // Cập nhật slug form từ hồ sơ (nếu có)
        if (data.form_view_slug) {
          this.currentFormSlug = data.form_view_slug;
          await this.fetchFields();
        }

        // Orphan fields and object sections are now correctly loaded.
        // Removed auto-entity creation to avoid garbage data as requested.

      } catch (e) {
        console.error('Lỗi load hồ sơ:', e);
        this.showError(e, 'Không tải được dữ liệu hồ sơ');
      } finally {
        this.loading = false;
      }
    },
    async saveProfile(silent = false) {
      // 0. Kiểm tra hồ sơ khóa
      if (this.profileStatus === 'FINALIZED') {
        if (!silent) this.$toast.warning("Hồ sơ đang khóa, không thể update");
        return;
      }

      if (!this.profileName) {
        if (!silent) this.showWarning('Vui lòng nhập tên hồ sơ!', 'Thiếu thông tin');
        return;
      }

      // 1. Kiểm tra TRÙNG LẶP MASTER (Phase 1.3 - Snapshot principle)
      // LUÔN kiểm tra, kể cả khi auto-save (silent) để đảm bảo không "lén" lưu đối tượng trùng mà không xác nhận
      const dupes = [];
      Object.keys(this.objectSections).forEach(typeCode => {
        const items = this.objectSections[typeCode] || [];
        items.forEach(item => {
          if (item.master_object?._duplicateMasterId) {
            const val = item.master_object._duplicateValue;
            // Chỉ bắt xác nhận nếu giá trị này KHÁC với giá trị đã được xác nhận lần trước cho đối tượng này
            if (this.lastConfirmedDuplicateValues[item._uid] !== val) {
              dupes.push({
                _uid: item._uid,
                type: this.objectTypes.find(t => t.code === typeCode)?.name || typeCode,
                value: val,
                name: item.master_object._duplicateDisplayName,
                master_object: item.master_object
              });
            }
          }
        });
      });

      if (dupes.length > 0) {
        this.duplicateConfirmList = dupes;
        this.pendingSaveSilent = silent;
        // Nếu là auto-save, ta vẫn hiện modal để ép người dùng phải đối mặt với việc trùng lặp
        this.showDuplicateConfirmModal = true;
        return; // Dừng lại chờ xác nhận
      }

      await this.performSaveProfile(silent);
    },
    async performSaveProfile(silent = false) {
      // Đánh dấu các giá trị trùng lặp này đã được xác nhận để không hiện modal lần sau (cho đến khi đổi giá trị)
      this.duplicateConfirmList.forEach(dupe => {
        if (dupe._uid && dupe.value) {
          this.lastConfirmedDuplicateValues[dupe._uid] = dupe.value;
        }
      });

      this.showDuplicateConfirmModal = false;
      if (!silent) this.isSaving = true;
      try {
        let targetId = this.currentId;
        if (!targetId) {
          const createRes = await axios.post(`${API_URL}/loan-profiles/`, { name: this.profileName });
          targetId = createRes.data.id;
        }

        const payload = {
          name: this.profileName,
          field_values: this.generalFieldValues,
          object_sections: this.objectSections, // MỚI: Gửi object_sections
          form_slug: this.$route.query.form || this.currentFormSlug,
          is_auto_save: silent
        };
        const response = await axios.post(`${API_URL}/loan-profiles/${targetId}/save_form_data/`, payload);

        // Update local state with fresh data (contains IDs)
        if (response.data && response.data.id) {
          const data = response.data;
          this.profileName = data.name;
          this.profileStatus = data.status || 'DRAFT';
          this.currentId = data.id;

          // Chặn computed-update khi gán dữ liệu mới từ server
          this.suppressComputedUpdate = true;
          this.generalFieldValues = data.field_values || {};
          this.objectSections = data.object_sections || {};
          this.$nextTick(() => { this.suppressComputedUpdate = false; });

          // REDIRECT logic: Nếu đang ở màn hình tạo mới, chuyển sang màn hình chỉnh sửa
          if (!this.id && targetId && !silent) {
            console.log("DEBUG: Redirecting to edit mode for newly created profile:", targetId);
            this.$router.push(`/edit/${targetId}`);
          }
        }

        if (!silent) {
          this.$toast.success('Hồ sơ đã được lưu thành công');
        } else {
          console.log("Auto-save completed at " + new Date().toLocaleTimeString());
        }

        // Refresh relations to ensure latest links are shown
        this.relationRefreshTrigger++;
      } catch (error) {
        if (error.response && error.response.status === 423) {
          this.editingLockedBy = error.response.data.locked_by;
          if (!silent) this.$toast.error(`Không thể lưu! Hồ sơ hiện đang bị chỉnh sửa bởi ${this.editingLockedBy}`);
        } else {
          if (!silent) this.showError(error, 'Lỗi khi lưu');
          else console.error("Auto-save failed:", error);
        }
      } finally {
        if (!silent) this.isSaving = false;
      }
    },
    validateInternalDuplicates() {
      if (!this.objectTypes || this.objectTypes.length === 0) return true;
      let errors = [];

      // A. Kiểm tra trùng lặp Người
      const personType = this.objectTypes.find(t => t.code === 'PERSON');
      const peopleIdentities = new Set();
      if (personType && personType.identity_field_key) {
        const idKey = personType.identity_field_key;
        const people = this.objectSections['PERSON'] || [];
        for (const p of people) {
          const idValue = p.individual_field_values?.[idKey];
          if (idValue) {
            if (peopleIdentities.has(idValue)) {
              errors.push(`Người trùng ${personType.name} (${idValue})`);
            }
            peopleIdentities.add(idValue);
          }
        }
      }

      // B. Kiểm tra trùng lặp Tài sản
      const assetIdentities = {};
      const assetList = this.computedAssetList;
      for (const a of assetList) {
        const typeCode = a.master_object?.object_type || a._originalType;
        if (!typeCode) continue;

        const typeConfig = this.objectTypes.find(t => t.code === typeCode);
        if (!typeConfig || !typeConfig.identity_field_key) continue;

        const idKey = typeConfig.identity_field_key;
        const idValue = a.individual_field_values?.[idKey] || a.asset_field_values?.[idKey];

        if (idValue) {
          if (!assetIdentities[typeCode]) assetIdentities[typeCode] = new Set();
          if (assetIdentities[typeCode].has(idValue)) {
            errors.push(`Tài sản ${typeConfig.name} trùng mã (${idValue})`);
          }
          assetIdentities[typeCode].add(idValue);
        }
      }

      if (errors.length > 0) {
        // Hiển thị thông báo tổng hợp
        this.$toast.warning(`LỖI TRÙNG LẶP: \n- ${errors.join('\n- ')} \nVui lòng kiểm tra lại.`);
        return false;
      }

      return true;
    },
    openDownloadModal() {
      this.isDownloadModalOpen = true;
    },
    async lockProfile() {
      this.showLockPasswordModal = true;
    },
    async handleLockPassword(password) {
      this.showLockPasswordModal = false;
      if (!password) return;

      try {
        await axios.post(`${API_URL}/loan-profiles/${this.id || this.currentId}/lock_profile/`, { password });
        this.profileStatus = 'FINALIZED';
        this.$toast.success("Hồ sơ đã được khóa.");
      } catch (e) {
        this.showLockPasswordModal = false;
        this.showError(e, 'Lỗi khi khóa hồ sơ');
      }
    },
    async unlockProfile() {
      this.showUnlockPasswordModal = true;
    },
    async handleUnlockPassword(password) {
      this.showUnlockPasswordModal = false;
      if (!password) return;

      try {
        await axios.post(`${API_URL}/loan-profiles/${this.id || this.currentId}/unlock_profile/`, { password });
        this.profileStatus = 'DRAFT';
        this.$toast.success("Hồ sơ đã được mở khóa.");
      } catch (e) {
        this.showUnlockPasswordModal = false;
        this.showError(e, 'Lỗi khi mở khóa');
      }
    },
    async acquireLock() {
      if (!this.id && !this.currentId) return;
      const pid = this.id || this.currentId;
      try {
        const res = await axios.post(`${API_URL}/loan-profiles/${pid}/acquire_lock/`);
        if (res.data.locked) {
          this.editingLockedBy = res.data.locked_by;
          this.stopHeartbeat();
        } else {
          this.editingLockedBy = null;
          this.startHeartbeat(pid);
        }
      } catch (e) {
        if (e.response && e.response.status === 423) {
          this.editingLockedBy = e.response.data.locked_by;
        }
      }
    },
    startHeartbeat(pid) {
      if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = setInterval(async () => {
        try {
          await axios.post(`${API_URL}/loan-profiles/${pid}/heartbeat/`);
        } catch (e) {
          console.error("Heartbeat failed", e);
          this.stopHeartbeat();
        }
      }, 300000); // 5 minutes
    },
    stopHeartbeat() {
      if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    },
    async releaseLock() {
      if (this.editingLockedBy || (!this.id && !this.currentId)) return;
      const pid = this.id || this.currentId;
      try {
        await axios.post(`${API_URL}/loan-profiles/${pid}/release_lock/`);
      } catch (e) {
        console.error("Release lock failed", e);
      }
    }
  }
};
</script>

<style scoped>
.form-layout {
  display: flex;
  user-select: none;
}

.header-title {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
  flex: 3;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 5px;
}

.profile-id-badge {
  background: #34495e;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: bold;
  font-size: 1.1rem;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.profile-name-label {
  font-weight: bold;
  color: #555;
  white-space: nowrap;
}

.profile-name-input-wrapper {
  flex: 1;
  max-width: 600px;
}

.profile-name-input {
  width: 100%;
  font-size: 1.25rem;
  padding: 8px 0;
  border: none;
  border-bottom: 2px solid #ccc;
  outline: none;
  font-weight: 500;
  transition: border-color 0.2s;
}

.profile-name-input:focus {
  border-bottom-color: #42b983;
}

.form-type-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #e1f5fe;
  color: #f6142f;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9em;
  border: 1px solid #f40606;
}

.badge-label {
  font-weight: 600;
  opacity: 0.8;
}

.badge-value {
  font-weight: bold;
}

/* Panels resizing */
.resize-handle {
  width: 6px;
  background-color: var(--slate-200);
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
  z-index: 100;
}

.resize-handle:hover {
  background-color: var(--color-primary);
}

.handle-icon {
  font-size: 10px;
  color: var(--slate-400);
  user-select: none;
}

.left-panel,
.right-panel {
  overflow-y: auto;
  padding: var(--spacing-md);
}

.form-layout {
  display: flex;
  height: calc(100vh - 120px);
  background-color: var(--slate-50);
}

.profile-id-badge {
  background: var(--slate-200);
  color: var(--slate-700);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 700;
}

.profile-name-input {
  border: none;
  background: transparent;
  font-size: var(--font-lg);
  font-weight: 700;
  color: var(--color-text);
  width: 550px;
  border-bottom: 2px solid transparent;
  transition: var(--transition-fast);
}

.profile-name-input:focus {
  outline: none;
  border-bottom-color: var(--color-primary);
}

/* --- History Drawer Styles --- */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(2px);
  z-index: 2000;
}

.drawer-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 450px;
  background: white;
  z-index: 2001;
  box-shadow: var(--shadow-xl);
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
}

.drawer-panel.is-open {
  transform: translateX(0);
}

.drawer-header {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--slate-50);
}

.drawer-header h3 {
  margin: 0;
  font-size: var(--font-lg);
  font-weight: 700;
  color: var(--slate-800);
}

.btn-close-drawer {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--slate-400);
  transition: var(--transition-fast);
}

.btn-close-drawer:hover {
  color: var(--color-danger);
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  background: white;
}

/* Standardized styles are now using global classes from common-ui.css */
.duplicate-comparison-table.data-table {
  border: 1px solid var(--color-border);
  margin-bottom: var(--spacing-lg);
}

.current-input {
  color: var(--color-danger);
  font-weight: 700;
}

.master-data {
  background: var(--slate-50);
}

.master-name {
  font-weight: 600;
  color: var(--slate-900);
}

.master-id {
  font-size: 0.8rem;
  color: var(--slate-500);
}
</style>

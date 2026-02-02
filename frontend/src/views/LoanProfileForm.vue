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
        <button v-if="profileStatus === 'DRAFT' && (id || currentId)" class="btn-action btn-lock"
          @click="lockProfile">🔒 Khóa hồ
          sơ</button>
        <button v-if="profileStatus === 'FINALIZED'" class="btn-action btn-unlock" @click="unlockProfile">🔓 Mở
          khóa</button>
        <button v-if="id || currentId" class="btn-action btn-doc" @click="openDownloadModal">Xuất HĐ</button>
        <button v-if="id || currentId" class="btn-action btn-copy" @click="openDuplicateModal">Nhân bản</button>
        <button class="btn-action btn-primary" @click="saveProfile" :disabled="isSaving">
          {{ isSaving ? 'Đang lưu...' : 'Lưu Hồ Sơ' }}
        </button>
      </div>
    </header>

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
              :idPrefix="`gen-l-${segment.id}-`" />
          </div>

          <!-- Type: DEDICATED (Khu vực riêng - VD: Hợp đồng) -->
          <div v-if="segment.type === 'DEDICATED'" class="panel-section dedicated-section">
            <div class="panel-header">
              <h3>{{ segment.name }}</h3>
              <div class="header-actions">
                <button class="btn-action btn-secondary btn-sm" @click="openSelectModal(segment.code)">🔍 Tìm &
                  Chọn</button>
                <button class="btn-action btn-secondary btn-sm" @click="addEntity(segment.code)">+ Thêm mới</button>
              </div>
            </div>

            <!-- Trường hợp: Các đối tượng (Asset List/Dedicated List) -->
            <div v-if="!objectSections[segment.code] || objectSections[segment.code].length === 0" class="empty-state">
              Chưa có thông tin {{ segment.name }}. Nhấn 'Tìm & Chọn' hỗ trợ nhập nhanh.
            </div>

            <div v-for="(item, index) in objectSections[segment.code]" :key="segment.code + '-' + index"
              class="master-card generic-card">
              <div class="card-header-mini">
                <strong>{{ segment.name }} #{{ index + 1 }}</strong>
                <button class="btn-remove-mini" @click="removeEntity(segment.code, index)">&times;</button>
              </div>
              <DynamicForm :fields="getFieldsForType(segment.code)" v-model="item.individual_field_values"
                :disabled="isReadOnly" :idPrefix="`ded-${segment.code.toLowerCase()}-${index}-`" />

              <RelationManager v-if="item.master_object && item.master_object.id"
                :masterObjectId="item.master_object.id" :profileObjects="allSavedObjects" :currentObjectType="segment.code" :refreshTrigger="relationRefreshTrigger" :allFields="allFields" :disabled="isReadOnly" />
            </div>
          </div>

          <!-- Type: ASSET_LIST (Danh sách Tài sản) -->
          <div v-else-if="segment.type === 'ASSET_LIST'">
            <div class="panel-header">
              <h3>Danh sách Tài sản</h3>
              <button class="btn-action btn-secondary" @click="addEntity(null)">+ Thêm Tài sản</button>
            </div>
            <div v-if="getAssetList().length === 0" class="empty-state">Chưa có tài sản nào.</div>
            <div v-for="(asset, index) in getAssetList()" :key="'asset-' + index">
              <AssetForm :index="index" :asset="asset" :assetFields="getAssetFields()" :availableTypes="objectTypes"
                :profileObjects="allSavedObjects" :refreshTrigger="relationRefreshTrigger" :allFields="allFields" @update:asset="updateAssetList(index, $event)"
                @remove="removeAssetList(index)" />
            </div>
          </div>

          <!-- Type: PERSON_LIST (Danh sách Người liên quan) -->
          <div v-else-if="segment.type === 'PERSON_LIST'">
            <div class="panel-header">
              <h3>Danh sách Người liên quan</h3>
              <button class="btn-action btn-secondary" @click="addEntity('PERSON')">+ Thêm Người</button>
            </div>
            <div v-if="!objectSections['PERSON'] || objectSections['PERSON'].length === 0" class="empty-state">
              Chưa có người nào.
            </div>
            <div v-for="(person, index) in objectSections['PERSON']" :key="'person-' + index">
              <PersonForm :index="index" :person="person" :personFields="getFieldsForType('PERSON')"
                :availableRoles="availableRoles" :availableTypes="objectTypes" :profileObjects="allSavedObjects" :refreshTrigger="relationRefreshTrigger" :allFields="allFields"
                @update:person="updateEntity('PERSON', index, $event)" @remove="removeEntity('PERSON', index)" />
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
              :idPrefix="`gen-r-${segment.id}-`" />
          </div>

          <!-- Type: DEDICATED (Khu vực riêng - VD: Hợp đồng) -->
          <div v-if="segment.type === 'DEDICATED'" class="panel-section dedicated-section">
            <div class="panel-header">
              <h3>{{ segment.name }}</h3>
              <div class="header-actions">
                <button class="btn-action btn-secondary btn-sm" @click="openSelectModal(segment.code)">🔍 Tìm &
                  Chọn</button>
                <button class="btn-action btn-secondary btn-sm" @click="addEntity(segment.code)">+ Thêm mới</button>
              </div>
            </div>

            <!-- Trường hợp: Các đối tượng -->
            <div v-if="!objectSections[segment.code] || objectSections[segment.code].length === 0" class="empty-state">
              Chưa có thông tin {{ segment.name }}. Nhấn 'Tìm & Chọn' hỗ trợ nhập nhanh.
            </div>

            <div v-for="(item, index) in objectSections[segment.code]" :key="segment.code + '-' + index"
              class="master-card generic-card">
              <div class="card-header-mini">
                <strong>{{ segment.name }} #{{ index + 1 }}</strong>
                <button class="btn-remove-mini" @click="removeEntity(segment.code, index)">&times;</button>
              </div>
              <DynamicForm :fields="getFieldsForType(segment.code)" v-model="item.individual_field_values"
                :disabled="isReadOnly" :idPrefix="`ded-${segment.code.toLowerCase()}-${index}-`" />

              <RelationManager v-if="item.master_object && item.master_object.id"
                :masterObjectId="item.master_object.id" :profileObjects="allSavedObjects" :currentObjectType="segment.code" :refreshTrigger="relationRefreshTrigger" :allFields="allFields" :disabled="isReadOnly" />
            </div>
          </div>

          <!-- Type: ASSET_LIST (Danh sách Tài sản) -->
          <div v-else-if="segment.type === 'ASSET_LIST'">
            <div class="panel-header">
              <h3>Danh sách Tài sản</h3>
              <button class="btn-action btn-secondary" @click="addEntity(null)">+ Thêm Tài sản</button>
            </div>
            <div v-if="getAssetList().length === 0" class="empty-state">Chưa có tài sản nào.</div>
            <div v-for="(asset, index) in getAssetList()" :key="'asset-' + index">
              <AssetForm :index="index" :asset="asset" :assetFields="getAssetFields()" :availableTypes="objectTypes"
                :profileObjects="allSavedObjects" :refreshTrigger="relationRefreshTrigger" :allFields="allFields" @update:asset="updateAssetList(index, $event)"
                @remove="removeAssetList(index)" />
            </div>
          </div>

          <!-- Type: PERSON_LIST (Danh sách Người liên quan) -->
          <div v-else-if="segment.type === 'PERSON_LIST'">
            <div class="panel-header">
              <h3>Danh sách Người liên quan</h3>
              <button class="btn-action btn-secondary" @click="addEntity('PERSON')">+ Thêm Người</button>
            </div>
            <div v-if="!objectSections['PERSON'] || objectSections['PERSON'].length === 0" class="empty-state">
              Chưa có người nào.
            </div>
            <div v-for="(person, index) in objectSections['PERSON']" :key="'person-' + index">
              <PersonForm :index="index" :person="person" :personFields="getFieldsForType('PERSON')"
                :availableRoles="availableRoles" :availableTypes="objectTypes" :profileObjects="allSavedObjects" :refreshTrigger="relationRefreshTrigger" :allFields="allFields"
                @update:person="updateEntity('PERSON', index, $event)" @remove="removeEntity('PERSON', index)" />
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

    <!-- Modal tìm kiếm vạn năng -->
    <ObjectSelectModal :isOpen="showUniversalSelect" :type="currentSelectType" @select="handleUniversalSelect"
      @close="showUniversalSelect = false" />
  </div>
</template>

<script>
import axios from 'axios';
import DynamicForm from '../components/DynamicForm.vue';
import PersonForm from '../components/PersonForm.vue';
import AssetForm from '../components/AssetForm.vue';
import ConfirmModal from '../components/ConfirmModal.vue';
import InputModal from '../components/InputModal.vue';
import ContractDownloader from '../components/ContractDownloader.vue';
import ObjectSelectModal from '../components/ObjectSelectModal.vue';
import RelationManager from '../components/RelationManager.vue';
import { errorHandlingMixin } from '../utils/errorHandler';

export default {
  name: 'LoanProfileForm',
  components: {
    DynamicForm, PersonForm, AssetForm, ConfirmModal,
    InputModal, ContractDownloader, ObjectSelectModal,
    RelationManager
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
    };
  },
  computed: {
    isReadOnly() {
      return this.profileStatus === 'FINALIZED';
    },
    getSegmentsByPosition() {
      return (position) => {
        let segments = [];

        // 1. Nhóm các Trường mồ côi (Field Groups not linked to Object Types)
        const groups = this.allFields.reduce((acc, field) => {
          const gSlug = field.group_slug || 'other';
          const gPos = field.group_layout_position || 'LEFT';
          if (gPos !== position) return acc;

          // Chỉ lấy các trường "Mồ côi" (không gắn với Object Type nào)
          const specialTypes = field.group_allowed_object_types || [];
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
          // Khớp qua group (ưu tiên) hoặc trực tiếp qua field level links
          const groupMatch = f.group_allowed_object_types?.includes(typeCode);
          const fieldMatch = f.allowed_object_types?.includes(typeCode);
          return groupMatch || fieldMatch;
        });
      }
    },
    showRightPanel() {
      return this.rightPanelSegments.length > 0;
    },
    coreFields() {
      // Thông tin CỐT LÕI (CORE) = Các trường không thuộc bất kỳ object_type nào (General Profile)
      return this.allFields.filter(f => {
        const specialTypes = f.group_allowed_object_types || [];
        return specialTypes.length === 0;
      }).sort((a, b) => a.order - b.order);
    },
  },
  async mounted() {
    await this.fetchFields();
    this.fetchRoles();
    await this.fetchObjectTypes();
    if (this.id) {
      this.currentId = this.id;
      await this.fetchProfileData(this.id);
    }
    // ĐÃ XÓA: Tự động addEntity('PERSON') và addEntity(null) để tránh tạo rác
  },
  watch: {
    // Watchers for other logic if needed in future
    '$route.query.form': {
      handler() {
        this.fetchFields();
      }
    }
  },
  methods: {
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
        const res = await axios.get('http://127.0.0.1:8000/api/object-types/');
        this.objectTypes = res.data;
      } catch (e) { console.error("Lỗi load object types:", e); }
    },
    async fetchRoles() {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/roles/');
        this.availableRoles = res.data.map(r => r.name);
      } catch (e) { console.error("Lỗi load roles:", e); }
    },
    async fetchFields() {
      const form_slug = this.$route.query.form || this.currentFormSlug || "";
      try {
        const url = `http://127.0.0.1:8000/api/fields/?form_slug=${form_slug}`;
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
        const res = await axios.get(`http://127.0.0.1:8000/api/form-views/`);
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
        const specialTypes = field.group_allowed_object_types || [];
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

      // TRƯỜNG HỢP: Đổi loại đối tượng (VD: Từ BOND sang REALESTATE)
      if (newType && newType !== oldType) {
        console.log(`DEBUG: Moving object from ${oldType} to ${newType}`);

        // 1. Xóa khỏi mảng cũ
        this.objectSections[oldType].splice(index, 1);

        // 2. Thêm vào mảng mới
        if (!this.objectSections[newType]) {
          this.objectSections[newType] = [];
        }
        this.objectSections[newType].push(updated);

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

      this.objectSections[targetType].push({
        id: null,
        master_object: { object_type: typeCode }, // Có thể là null nếu typeCode=null
        individual_field_values: { ...defaults },
        roles: targetType === 'ATTORNEY' ? ['đại diện'] : []
      });

      // Auto-save if profile exists
      if (this.currentId) {
        await this.saveProfile();
      } else {
        // For new profiles, just refresh the list which will update IDs
        // No specific action needed as saveProfile handles navigation or data refresh
      }

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
    getAssetList() {
      const list = [];
      const seenTypes = new Set();

      this.assetListTypes.forEach(t => {
        seenTypes.add(t);
        if (this.objectSections[t]) {
          this.objectSections[t].forEach((item, idx) => {
            list.push({ ...item, _originalType: t, _originalIdx: idx });
          });
        }
      });

      // Luôn bao gồm ngăn chứa 'ASSET' (ngăn chứa chung ban đầu)
      if (!seenTypes.has('ASSET') && this.objectSections['ASSET']) {
        this.objectSections['ASSET'].forEach((item, idx) => {
          list.push({ ...item, _originalType: 'ASSET', _originalIdx: idx });
        });
      }
      return list;
    },
    getAssetFields() {
      // Lấy tất cả các fields thuộc về bất kỳ loại tài sản nào trong assetListTypes
      return this.allFields.filter(f => {
        const types = f.group_allowed_object_types || [];
        // Nếu không có types đặc thù -> Không phải field tài sản
        if (types.length === 0) return false;
        // Kiểm tra xem có trùng với bất kỳ loại ASSET_LIST nào không
        return types.some(t => this.assetListTypes.includes(t));
      });
    },
    updateAssetList(index, updated) {
      const list = this.getAssetList();
      const target = list[index];
      if (target) {
        this.updateEntity(target._originalType, target._originalIdx, updated);
      }
    },
    removeAssetList(index) {
      const list = this.getAssetList();
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
          `http://127.0.0.1:8000/api/loan-profiles/${this.id}/duplicate/`,
          { new_name: newName }
        );
        this.showDuplicateModal = false;
        this.$toast.success(`Đã tạo bản sao: ${response.data.name}`);
        // Chuyển hướng sang hồ sơ mới
        this.$router.push(`/edit/${response.data.id}`);
        // Vì Vue reuse component khi route thay đổi id, ta cần load lại data
        this.fetchProfileData(response.data.id);
      } catch (error) {
        console.error(error);
        this.showError(error, 'Lỗi khi tạo bản sao');
      }
    },

    async fetchProfileData(id) {
      try {
        this.loading = true;
        const response = await axios.get(`http://127.0.0.1:8000/api/loan-profiles/${id}/`);
        const data = response.data;
        this.profileName = data.name;
        this.profileStatus = data.status || 'DRAFT';
        this.generalFieldValues = data.field_values || {};

        // MỚI: Load object_sections thay vì people/assets
        this.objectSections = data.object_sections || {};

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
    async saveProfile() {
      // 0. Kiểm tra hồ sơ khóa
      if (this.profileStatus === 'FINALIZED') {
        this.$toast.warning("Hồ sơ đang khóa, không thể update");
        return;
      }

      if (!this.profileName) {
        this.showWarning('Vui lòng nhập tên hồ sơ!', 'Thiếu thông tin');
        return;
      }
      this.isSaving = true;
      try {
        let targetId = this.currentId;
        if (!targetId) {
          const createRes = await axios.post('http://127.0.0.1:8000/api/loan-profiles/', { name: this.profileName });
          targetId = createRes.data.id;
        }

        const payload = {
          name: this.profileName,
          field_values: this.generalFieldValues,
          object_sections: this.objectSections, // MỚI: Gửi object_sections
          form_slug: this.$route.query.form || this.currentFormSlug
        };
        const response = await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${targetId}/save_form_data/`, payload);

        // Update local state with fresh data (contains IDs)
        if (response.data && response.data.id) {
          const data = response.data;
          this.profileName = data.name;
          this.profileStatus = data.status || 'DRAFT';
          this.generalFieldValues = data.field_values || {};
          this.objectSections = data.object_sections || {};
        }

        // Cập nhật currentId nếu là hồ sơ mới tạo thành công
        if (!this.currentId) {
          this.currentId = targetId;
        }

        this.$toast.success('Lưu thành công!');
        // KHÔNG chuyển trang nữa theo yêu cầu của User
        // this.$router.push('/');
        
        // Refresh relations to ensure latest links are shown
        this.relationRefreshTrigger++;
      } catch (error) {
        console.error(error);
        this.$toast.error('Lỗi khi lưu: ' + (error.response?.data?.message || error.message));
      } finally {
        this.isSaving = false;
      }
    },
    validateInternalDuplicates() {
      if (!this.objectTypes || this.objectTypes.length === 0) return true; // Tránh lỗi khi chưa load xong

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
              this.$toast.warning(`LỖI: Hồ sơ đang có 2 Người trùng ${personType.name} (${idValue}). Vui lòng kiểm tra lại.`);
              return false;
            }
            peopleIdentities.add(idValue);
          }
        }
      }

      // B. Kiểm tra trùng lặp Tài sản (theo identity_field_key của từng loại)
      const assetIdentities = {}; // { object_type: Set(values) }
      const assetList = this.getAssetList();
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
            this.$toast.warning(`LỖI: Hồ sơ đang có 2 tài sản ${typeConfig.name} trùng mã định danh (${idValue}). Vui lòng kiểm tra lại.`);
            return false;
          }
          assetIdentities[typeCode].add(idValue);
        }
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
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${this.id || this.currentId}/lock_profile/`, { password });
        this.profileStatus = 'FINALIZED';
        this.$toast.success("Hồ sơ đã được khóa.");
      } catch (e) {
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
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${this.id || this.currentId}/unlock_profile/`, { password });
        this.profileStatus = 'DRAFT';
        this.$toast.success("Hồ sơ đã được mở khóa.");
      } catch (e) {
        this.showError(e, 'Lỗi khi mở khóa');
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
  max-width: 400px;
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
  width: 5px;
  background-color: #ddd;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.resize-handle:hover,
.resize-handle:active {
  background-color: #42b983;
}

.left-panel {
  overflow-y: auto;
  padding-right: 5px;
}

.right-panel {
  overflow-y: auto;
  padding-left: 5px;
}

.panel-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #eee;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.panel-section h3,
.panel-header h3 {
  margin: 0;
  color: #2c3e50;
  border-bottom: 2px solid #42b983;
  padding-bottom: 5px;
  display: inline-block;
}

.empty-state {
  padding: 40px;
  text-align: center;
  background: #eee;
  color: #777;
  border-radius: 8px;
  border: 2px dashed #ccc;
}

.attorney-section {
  border-left: 5px solid #3498db;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.85em;
}

.attorney-card,
.generic-card {
  background: #fff;
  border: 1px solid #d1e9f9;
  border-radius: 6px;
  padding: 15px;
  margin-top: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.dedicated-section {
  border-left: 5px solid #3498db;
}

.card-header-mini {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px dashed #3498db;
  color: #3498db;
}

.btn-remove-mini {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #e74c3c;
  cursor: pointer;
  line-height: 1;
  padding: 0 5px;
}

.btn-remove-mini:hover {
  color: #c0392b;
  transform: scale(1.2);
}
</style>

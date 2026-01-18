<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-title">
        <label class="profile-name-label">Tên hồ sơ:</label>
        <div class="profile-name-input-wrapper">
          <input v-model="profileName" class="profile-name-input" placeholder="Nhập tên hồ sơ..."
            :disabled="isReadOnly" />
        </div>
        <div v-if="profileStatus" class="status-badge" :class="profileStatus.toLowerCase()">
          {{ profileStatus === 'FINALIZED' ? '🔒 ĐÃ KHÓA' : '✍️ NHÁP' }}
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
      <!-- CỘT TRÁI: THÔNG TIN CHUNG + NGƯỜI (Default) + Asset (Nếu config Left) -->
      <div class="left-panel" :style="{ width: (showRightPanel ? leftPanelWidth : 100) + '%' }">
        <div v-for="(group, slug) in leftPanelGroups" :key="slug" class="panel-section">
          <h3>{{ group.name }}</h3>
          <DynamicForm :fields="group.fields" v-model="generalFieldValues" :disabled="isReadOnly" />
        </div>

        <!-- DANH SÁCH NGƯỜI (CỘT TRÁI - Default) -->
        <div v-if="!isPersonRight && personFields.length > 0">
          <div class="panel-header">
            <h3>Danh sách Người liên quan</h3>
            <button class="btn-action btn-secondary" @click="addPerson">+ Thêm Người</button>
          </div>

          <div v-if="people.length === 0" class="empty-state">
            Chưa có người nào. Hãy thêm Bên vay hoặc Bên bảo đảm.
          </div>

          <div v-for="(person, index) in people" :key="'person-' + index">
            <PersonForm :index="index" :person="person" :personFields="personFields" :availableRoles="availableRoles"
              :availableTypes="objectTypes" @update:person="updatePerson(index, $event)"
              @remove="removePerson(index)" />
          </div>
        </div>

        <!-- Asset List (Nếu config Left) -->
        <div v-if="!isAssetRight && assetFields.length > 0">
          <div class="panel-header">
            <h3>Danh sách Tài sản</h3>
            <button class="btn-action btn-secondary" @click="addAsset">+ Thêm Tài sản</button>
          </div>
          <div v-if="assets.length === 0" class="empty-state">Chưa có tài sản nào.</div>
          <div v-for="(asset, index) in assets" :key="'asset-' + index">
            <AssetForm :index="index" :asset="asset" :assetFields="assetFields" :availableTypes="objectTypes"
              @update:asset="updateAsset(index, $event)" @remove="removeAsset(index)" />
          </div>
        </div>
      </div>

      <!-- THANH KÉO (DRAG HANDLE) -->
      <div class="resize-handle" @mousedown="startResize" v-if="showRightPanel">
        <div class="handle-icon">||</div>
      </div>

      <!-- CỘT PHẢI: DANH SÁCH TÀI SẢN -->
      <!-- CỘT PHẢI: GROUP PHẢI + NGƯỜI (NẾU CÓ) + TÀI SẢN (NẾU CÓ) -->
      <div class="right-panel" :style="{ width: (100 - leftPanelWidth) + '%' }" v-if="showRightPanel">

        <!-- Các nhóm Generic bên phải -->
        <div v-for="(group, slug) in rightPanelGroups" :key="'right-' + slug" class="panel-section">
          <h3>{{ group.name }}</h3>
          <DynamicForm :fields="group.fields" v-model="generalFieldValues" :disabled="isReadOnly" />
        </div>

        <!-- Person List (nếu config Right) -->
        <div v-if="isPersonRight && personFields.length > 0">
          <div class="panel-header">
            <h3>Danh sách Người liên quan</h3>
            <button class="btn-action btn-secondary" @click="addPerson">+ Thêm Người</button>
          </div>
          <div v-if="people.length === 0" class="empty-state">Chưa có người nào.</div>
          <div v-for="(person, index) in people" :key="'person-' + index">
            <PersonForm :index="index" :person="person" :personFields="personFields" :availableRoles="availableRoles"
              :availableTypes="objectTypes" @update:person="updatePerson(index, $event)"
              @remove="removePerson(index)" />
          </div>
        </div>

        <!-- Asset List (Default Right, unless config Left) -->
        <div v-if="isAssetRight && assetFields.length > 0">
          <div class="panel-header">
            <h3>Danh sách Tài sản</h3>
            <button class="btn-action btn-secondary" @click="addAsset">+ Thêm Tài sản</button>
          </div>
          <div v-if="assets.length === 0" class="empty-state">Chưa có tài sản nào.</div>
          <div v-for="(asset, index) in assets" :key="'asset-' + index">
            <AssetForm :index="index" :asset="asset" :assetFields="assetFields" :availableTypes="objectTypes"
              @update:asset="updateAsset(index, $event)" @remove="removeAsset(index)" />
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal :visible="showDeleteModal" :title="deleteModalTitle" :message="deleteModalMessage" confirmText="Xóa"
      @confirm="confirmDelete" @cancel="showDeleteModal = false" />

    <!-- Duplicate Modal -->
    <InputModal :visible="showDuplicateModal" title="Tạo bản sao hồ sơ" label="Tên hồ sơ mới:"
      :defaultValue="duplicateDefaultName" confirmText="Tạo bản sao" @confirm="confirmDuplicate"
      @cancel="showDuplicateModal = false" />

    <!-- Contract Downloader Modal -->
    <ContractDownloader :isOpen="isDownloadModalOpen" :profileId="Number(currentId || id)" :profileName="profileName"
      @close="isDownloadModalOpen = false" />
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

export default {
  name: 'LoanProfileForm',
  components: { DynamicForm, PersonForm, AssetForm, ConfirmModal, InputModal, ContractDownloader },
  props: ['id'],
  data() {
    return {
      loading: true,
      isSaving: false,
      allFields: [],
      profileName: '',
      generalFieldValues: {},
      people: [],
      assets: [], // Danh sách tài sản
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

      // Profile Status
      profileStatus: 'DRAFT'
    };
  },
  computed: {
    isReadOnly() {
      return this.profileStatus === 'FINALIZED';
    },
    getGroupsByPosition() {
      return (position) => {
        return this.allFields.reduce((groups, field) => {
          const gName = field.group_name || 'Khác';
          const gSlug = field.group_slug || 'other';
          const gPos = field.group_layout_position || 'LEFT'; // Mặc định Trái

          // Nếu lọc theo vị trí mà không khớp -> bỏ qua
          if (gPos !== position) return groups;

          // Lọc bỏ các nhóm đặc biệt (CÓ gán allowed_object_types) khỏi luồng hiển thị Generic
          // Nhóm gán object types sẽ được hiển thị qua PersonForm hoặc AssetForm
          if (field.group_allowed_object_types && field.group_allowed_object_types.length > 0) {
            return groups;
          }

          if (!groups[gSlug]) groups[gSlug] = { name: gName, fields: [] };
          groups[gSlug].fields.push(field);
          return groups;
        }, {});
      };
    },
    leftPanelGroups() {
      return this.getGroupsByPosition('LEFT');
    },
    rightPanelGroups() {
      return this.getGroupsByPosition('RIGHT');
    },
    isPersonRight() {
      // Check if any Person group is set to Right
      return this.personFields.some(f => f.group_layout_position === 'RIGHT');
    },
    isAssetRight() {
      // Default Assets to Right unless explicitly set to Left
      if (this.assetFields.length === 0) return true;
      // If ANY asset group is LEFT, should we move all to left? Or just stick to default Right?
      // Let's say if ALL are Left, move to Left. If ANY is Right (or default), keep Right.
      // Actually user requested Explicit control.
      // Logic: If the first asset group found is Left, move layout to Left.
      const first = this.assetFields[0];
      return first ? (first.group_layout_position === 'RIGHT') : true;
    },
    showRightPanel() {
      return (this.assetFields.length > 0 && this.isAssetRight) ||
        (this.personFields.length > 0 && this.isPersonRight) ||
        Object.keys(this.rightPanelGroups).length > 0;
    },
    coreFields() {
      // Thông tin CHUNG = Không có object_type hoặc rỗng (Core)
      return this.allFields.filter(f => !f.group_allowed_object_types || f.group_allowed_object_types.length === 0)
        .sort((a, b) => a.order - b.order);
    },
    personFields() {
      // Thông tin NGƯỜI = group có PERSON trong allowed_object_types
      return this.allFields.filter(f => f.group_allowed_object_types?.includes('PERSON'));
    },
    assetFields() {
      // Thông tin TÀI SẢN = group có object types nhưng không phải chỉ PERSON
      return this.allFields.filter(f => {
        const types = f.group_allowed_object_types || [];
        // Có ít nhất 1 type và không phải là duy nhất PERSON
        return types.length > 0 && !(types.length === 1 && types[0] === 'PERSON');
      });
    }
  },
  async mounted() {
    await this.fetchFields(); // Chờ load xong fields trước khi làm tiếp
    this.fetchRoles();
    this.fetchObjectTypes(); // New: Fetch object types
    if (this.id) {
      this.currentId = this.id;
      this.fetchProfileData(this.id);
    } else {
      // Đã có fields rồi nên gọi addPerson/addAsset ở đây sẽ có default values
      if (this.people.length === 0) this.addPerson();
      if (this.assets.length === 0) this.addAsset();
    }
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

        // MỞ RỘNG: Áp dụng giá trị mặc định cho cả Người và Tài sản (truy thu cho hồ sơ cũ)
        this.people.forEach(p => {
          const defaults = this.getDefaultValuesFor(this.personFields);
          const currentValues = p.individual_field_values || {};
          Object.keys(defaults).forEach(key => {
            if (!currentValues[key]) currentValues[key] = defaults[key];
          });
          p.individual_field_values = { ...currentValues };
        });

        this.assets.forEach(a => {
          const defaults = this.getDefaultValuesFor(this.assetFields);
          const currentValues = a.asset_field_values || {};
          Object.keys(defaults).forEach(key => {
            if (!currentValues[key]) currentValues[key] = defaults[key];
          });
          a.asset_field_values = { ...currentValues };
        });
      } catch (e) {
        console.error(e);
        alert('Lỗi tải cấu hình fields');
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
      // Áp dụng giá trị mặc định cho tất cả các trường KHÔNG thuộc nhóm Người hoặc Tài sản
      const currentValues = { ...this.generalFieldValues };
      this.allFields.forEach(field => {
        const isPersonGroup = (field.group_slug === 'thong-tin-ca-nhan' || field.group_slug === 'khach-hang');
        const isAssetGroup = (field.group_slug || '').startsWith('tai-san');

        if (!isPersonGroup && !isAssetGroup) {
          if (field.default_value && !currentValues[field.placeholder_key]) {
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
    // Person Actions
    addPerson() {
      const personDefaults = this.getDefaultValuesFor(this.personFields);
      this.people.push({
        id: null,
        ho_ten: '', // Xóa phần gán cứng, tất cả sẽ lấy từ personDefaults bên dưới
        cccd_so: '',
        roles: [],
        individual_field_values: { ...personDefaults }
      });
      // Nếu personDefaults có ho_ten hoặc cccd_so thì nó sẽ tự map vào form nhờ v-model
    },
    removePerson(index) {
      const person = this.people[index];
      const name = person.individual_field_values?.ho_ten || `Người #${index + 1}`;
      this.deleteModalTitle = 'Xác nhận xóa';
      this.deleteModalMessage = `Bạn có chắc muốn xóa '${name}' khỏi hồ sơ?`;
      this.deleteAction = 'person';
      this.deleteIndex = index;
      this.showDeleteModal = true;
    },
    updatePerson(index, updated) { this.people[index] = updated; },

    // Asset Actions
    addAsset() {
      const assetDefaults = this.getDefaultValuesFor(this.assetFields);
      this.assets.push({
        id: null,
        master_object: { object_type: null },
        asset_field_values: { ...assetDefaults }
      });
    },
    removeAsset(index) {
      const asset = this.assets[index];
      const name = asset.asset_field_values?.ten_tai_san || `Tài sản #${index + 1}`;
      this.deleteModalTitle = 'Xác nhận xóa';
      this.deleteModalMessage = `Bạn có chắc muốn xóa '${name}' khỏi hồ sơ?`;
      this.deleteAction = 'asset';
      this.deleteIndex = index;
      this.showDeleteModal = true;
    },
    confirmDelete() {
      if (this.deleteAction === 'person' && this.deleteIndex !== null) {
        this.people.splice(this.deleteIndex, 1);
      } else if (this.deleteAction === 'asset' && this.deleteIndex !== null) {
        this.assets.splice(this.deleteIndex, 1);
      }
      this.showDeleteModal = false;
      this.deleteAction = null;
      this.deleteIndex = null;
    },
    updateAsset(index, updated) { this.assets[index] = updated; },

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
        alert('Lỗi khi tạo bản sao!');
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
        this.people = data.people || [];
        this.assets = data.assets || [];

        // Cập nhật slug form từ hồ sơ (nếu có)
        if (data.form_view_slug) {
          this.currentFormSlug = data.form_view_slug;
          // Sau khi có form slug mới load lại fields cho đúng layout
          await this.fetchFields();
        }

        if (this.people.length === 0) this.addPerson();
        if (this.assets.length === 0) this.addAsset();

      } catch (e) {
        console.error('Lỗi load hồ sơ:', e);
        alert('Không tải được dữ liệu hồ sơ!');
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

      // 1. Kiểm tra trùng lặp nội bộ (Deduplication Check)
      if (!this.validateInternalDuplicates()) {
        return; // Dừng nếu có trùng lặp
      }

      if (!this.profileName) return alert('Vui lòng nhập tên hồ sơ!');
      this.isSaving = true;
      try {
        let targetId = this.currentId;
        if (!targetId) {
          const createRes = await axios.post('http://127.0.0.1:8000/api/loan-profiles/', { name: this.profileName });
          targetId = createRes.data.id;
        }

        // Filter out empty assets (no type selected)
        const validAssets = this.assets.filter(asset => {
          return asset.master_object && asset.master_object.object_type;
        });

        const payload = {
          name: this.profileName,
          field_values: this.generalFieldValues,
          people: this.people,
          assets: validAssets, // Use filtered assets
          form_slug: this.$route.query.form || this.currentFormSlug // Gửi kèm slug form để lưu
        };
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${targetId}/save_form_data/`, payload);

        // Cập nhật currentId nếu là hồ sơ mới tạo thành công
        if (!this.currentId) {
          this.currentId = targetId;
        }

        this.$toast.success('Lưu thành công!');
        // KHÔNG chuyển trang nữa theo yêu cầu của User
        // this.$router.push('/');
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
        for (const p of this.people) {
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
      for (const a of this.assets) {
        const typeCode = a.master_object?.object_type;
        if (!typeCode) continue;

        const typeConfig = this.objectTypes.find(t => t.code === typeCode);
        if (!typeConfig || !typeConfig.identity_field_key) continue;

        const idKey = typeConfig.identity_field_key;
        const idValue = a.asset_field_values?.[idKey];

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
      const password = prompt("Thiết lập mật khẩu để khóa hồ sơ này:");
      if (!password) return;

      try {
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${this.id || this.currentId}/lock_profile/`, { password });
        this.profileStatus = 'FINALIZED';
        this.$toast.success("Hồ sơ đã được khóa.");
      } catch (e) {
        alert("Lỗi khi khóa hồ sơ: " + (e.response?.data?.error || e.message));
      }
    },
    async unlockProfile() {
      const password = prompt("Nhập mật khẩu để mở khóa:");
      if (!password) return;

      try {
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${this.id || this.currentId}/unlock_profile/`, { password });
        this.profileStatus = 'DRAFT';
        this.$toast.success("Hồ sơ đã được mở khóa.");
      } catch (e) {
        alert("Lỗi khi mở khóa: " + (e.response?.data?.error || e.message));
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
</style>

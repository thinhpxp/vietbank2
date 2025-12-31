<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-title">
        <h2>Tạo / Cập nhật Hồ sơ Vay</h2>
        <div v-if="currentFormName" class="form-type-badge">
          <span class="badge-label">Mẫu hồ sơ:</span>
          <span class="badge-value">{{ currentFormName }}</span>
        </div>
      </div>
      <div class="header-buttons">
        <button v-if="id || currentId" class="btn-doc" @click="openDownloadModal">Xuất HĐ</button>
        <button v-if="id || currentId" class="btn-copy" @click="openDuplicateModal">Sao chép hồ sơ</button>
        <button class="btn-primary" @click="saveProfile" :disabled="isSaving">
          {{ isSaving ? 'Đang lưu...' : 'Lưu Hồ Sơ' }}
        </button>
      </div>
    </header>

    <div v-if="loading">Đang tải cấu hình...</div>

    <div v-else class="form-layout" ref="formLayout" @mousemove="onMouseMove" @mouseup="stopResize"
      @mouseleave="stopResize">
      <!-- CỘT TRÁI: THÔNG TIN CHUNG + NGƯỜI -->
      <div class="left-panel" :style="{ width: (assetFields.length > 0 ? leftPanelWidth : 100) + '%' }">
        <div class="panel-section" v-if="coreFields.length > 0">
          <h3>Thông tin Hồ sơ</h3>
          <!-- DynamicForm cho nhóm "Thông tin Hồ sơ" -->
          <DynamicForm :fields="coreFields" v-model="generalFieldValues" />
        </div>

        <div v-for="(fields, groupName) in groupedFields" :key="groupName" class="panel-section">
          <h3>{{ groupName }}</h3>
          <DynamicForm :fields="fields" v-model="generalFieldValues" />
        </div>

        <!-- DANH SÁCH NGƯỜI (GIỜ Ở CỘT TRÁI) -->
        <div v-if="personFields.length > 0">
          <div class="panel-header">
            <h3>Danh sách Người liên quan</h3>
            <button class="btn-secondary" @click="addPerson">+ Thêm Người</button>
          </div>

          <div v-if="people.length === 0" class="empty-state">
            Chưa có người nào. Hãy thêm Bên vay hoặc Bên bảo đảm.
          </div>

          <div v-for="(person, index) in people" :key="'person-' + index">
            <PersonForm :index="index" :person="person" :personFields="personFields" :availableRoles="availableRoles"
              @update:person="updatePerson(index, $event)" @remove="removePerson(index)" />
          </div>
        </div>
      </div>

      <!-- THANH KÉO (DRAG HANDLE) -->
      <div class="resize-handle" @mousedown="startResize" v-if="assetFields.length > 0">
        <div class="handle-icon">||</div>
      </div>

      <!-- CỘT PHẢI: DANH SÁCH TÀI SẢN -->
      <div class="right-panel" :style="{ width: (100 - leftPanelWidth) + '%' }" v-if="assetFields.length > 0">
        <div class="panel-header">
          <h3>Danh sách Tài sản</h3>
          <button class="btn-secondary" @click="addAsset">+ Thêm Tài sản</button>
        </div>

        <div v-if="assets.length === 0" class="empty-state">
          Chưa có tài sản nào.
        </div>

        <div v-for="(asset, index) in assets" :key="'asset-' + index">
          <AssetForm :index="index" :asset="asset" :assetFields="assetFields" @update:asset="updateAsset(index, $event)"
            @remove="removeAsset(index)" />
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
    <ContractDownloader :isOpen="isDownloadModalOpen" :profileId="currentId || id" :profileName="profileName"
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
      duplicateDefaultName: ''
    };
  },
  computed: {
    groupedFields() {
      return this.allFields.reduce((groups, field) => {
        const gName = field.group_name || 'Khác';
        const lowerGName = gName.toLowerCase();
        // Lọc bỏ Person + Asset + Core khỏi phần chung (sẽ hiển thị riêng)
        if (lowerGName === 'thông tin cá nhân' || lowerGName === 'khach_hang' ||
          lowerGName.includes('tài sản') || lowerGName.includes('hồ sơ')) {
          return groups;
        }

        if (!groups[gName]) {
          groups[gName] = [];
        }
        groups[gName].push(field);
        return groups;
      }, {});
    },
    coreFields() {
      // Lấy các trường thuộc nhóm "Thông tin Hồ sơ" (chứa ten_ho_so, ma_hd_the_chap, ma_hd_tin_dung)
      return this.allFields.filter(f => {
        const gName = (f.group_name || '').toLowerCase();
        return gName.includes('hồ sơ');
      }).sort((a, b) => a.order - b.order);
    },
    personFields() {
      return this.allFields.filter(f => {
        const gName = (f.group_name || '').toLowerCase();
        return gName === 'thông tin cá nhân' || gName === 'khach_hang';
      });
    },
    assetFields() {
      // Lấy các trường thuộc nhóm tài sản
      return this.allFields.filter(f => {
        const gName = (f.group_name || '').toLowerCase();
        return gName.includes('tài sản');
      });
    }
  },
  async mounted() {
    await this.fetchFields(); // Chờ load xong fields trước khi làm tiếp
    this.fetchRoles();
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
    // Sync profileName với generalFieldValues.ten_ho_so (two-way)
    'generalFieldValues.ten_ho_so': {
      handler(newVal) {
        if (newVal && newVal !== this.profileName) {
          this.profileName = newVal;
        }
      }
    },
    profileName: {
      handler(newVal) {
        if (newVal !== this.generalFieldValues.ten_ho_so) {
          this.generalFieldValues = { ...this.generalFieldValues, ten_ho_so: newVal };
        }
      }
    },
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
        const gName = (field.group_name || '').toLowerCase();
        const isPersonGroup = gName === 'thông tin cá nhân' || gName === 'khach_hang';
        const isAssetGroup = gName.includes('tài sản');

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
        alert(`Đã tạo bản sao: ${response.data.name}`);
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
      if (!this.profileName) return alert('Vui lòng nhập tên hồ sơ!');
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
          people: this.people,
          assets: this.assets,
          form_slug: this.$route.query.form || this.currentFormSlug // Gửi kèm slug form để lưu
        };
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${targetId}/save_form_data/`, payload);

        // Cập nhật currentId nếu là hồ sơ mới tạo thành công
        if (!this.currentId) {
          this.currentId = targetId;
        }

        alert('Lưu thành công!');
        // KHÔNG chuyển trang nữa theo yêu cầu của User
        // this.$router.push('/');
      } catch (error) {
        console.error(error);
        alert('Lỗi khi lưu: ' + (error.response?.data?.message || error.message));
      } finally {
        this.isSaving = false;
      }
    },
    openDownloadModal() {
      this.isDownloadModalOpen = true;
    }
  }
};
</script>

<style scoped>
.page-container {
  margin: 0 auto;
  padding: 20px;
  font-family: sans-serif;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-layout {
  display: flex;
  user-select: none;
  /* Tránh bôi đen text khi kéo chuột */
}

.header-title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

.header-title h2 {
  margin: 0;
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

/* Resize Handle Styles */
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

.handle-icon {
  font-size: 10px;
  color: #888;
  writing-mode: vertical-lr;
  /* Xoay chữ dọc */
}

/* Panels */
/* Lưu ý: width được set inline bởi Vue */
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

/* Collapsible Header Styles */
.section-header-row,
.header-left {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.header-left h3 {
  margin-right: 10px;
}

.section-header-row h3 {
  flex-grow: 1;
  margin: 0;
}

.toggle-icon {
  font-size: 12px;
  margin-left: 10px;
  transition: transform 0.2s;
  color: #666;
}

.toggle-icon.collapsed {
  transform: rotate(-90deg);
}

.panel-section h3,
.panel-header h3 {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 2px solid transparent;
  padding-bottom: 5px;
  display: inline-block;
}

/* Add border only when not collapsed if needed, or keep simpler */
.panel-section h3 {
  border-bottom: 2px solid #42b983;
}

.panel-header h3 {
  border-bottom: 2px solid #42b983;
}

.input-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.btn-primary {
  background: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background: #369870;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.btn-copy {
  background: #9b59b6;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-copy:hover {
  background: #8e44ad;
}

.btn-doc {
  background: #f39c12;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary {
  background: #2c3e50;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.empty-state {
  padding: 40px;
  text-align: center;
  background: #eee;
  color: #777;
  border-radius: 8px;
  border: 2px dashed #ccc;
}

.field-group {
  margin-bottom: 15px;
  text-align: left;
}

.field-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}
</style>
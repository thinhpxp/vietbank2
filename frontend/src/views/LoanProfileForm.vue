<template>
  <div class="page-container">
    <header class="page-header">
      <h2>Tạo / Cập nhật Hồ sơ Vay</h2>
      <button class="btn-primary" @click="saveProfile" :disabled="isSaving">
        {{ isSaving ? 'Đang lưu...' : 'Lưu Hồ Sơ' }}
      </button>
    </header>

    <div v-if="loading">Đang tải cấu hình...</div>

    <div v-else class="form-layout" ref="formLayout" @mousemove="onMouseMove" @mouseup="stopResize" @mouseleave="stopResize">
      <!-- CỘT TRÁI: THÔNG TIN CHUNG + NGƯỜI -->
      <div class="left-panel" :style="{ width: leftPanelWidth + '%' }">
        <div class="panel-section">
          <h3>Thông tin cơ bản</h3>
          <div class="field-group">
            <label>Tên hồ sơ <span style="color:red">*</span></label>
            <input 
              type="text" 
              v-model="profileName" 
              class="input-control" 
              placeholder="Nhập tên hồ sơ (VD: Hồ sơ ông A vay mua xe)..." 
            />
          </div>
        </div>

        <div v-for="(fields, groupName) in groupedFields" :key="groupName" class="panel-section">
          <h3>{{ groupName }}</h3>
          <DynamicForm
            :fields="fields"
            v-model="generalFieldValues"
          />
        </div>

        <!-- DANH SÁCH NGƯỜI (GIỜ Ở CỘT TRÁI) -->
        <div class="panel-header">
          <h3>Danh sách Người liên quan</h3>
          <button class="btn-secondary" @click="addPerson">+ Thêm Người</button>
        </div>

        <div v-if="people.length === 0" class="empty-state">
          Chưa có người nào. Hãy thêm Bên vay hoặc Bên bảo đảm.
        </div>

        <div v-for="(person, index) in people" :key="'person-'+index">
          <PersonForm
            :index="index"
            :person="person"
            :personFields="personFields"
            :availableRoles="availableRoles"
            @update:person="updatePerson(index, $event)"
            @remove="removePerson(index)"
          />
        </div>
      </div>

      <!-- THANH KÉO (DRAG HANDLE) -->
      <div class="resize-handle" @mousedown="startResize">
        <div class="handle-icon">||</div>
      </div>

      <!-- CỘT PHẢI: DANH SÁCH TÀI SẢN -->
      <div class="right-panel" :style="{ width: (100 - leftPanelWidth) + '%' }">
        <div class="panel-header">
          <h3>Danh sách Tài sản</h3>
          <button class="btn-secondary" @click="addAsset">+ Thêm Tài sản</button>
        </div>

        <div v-if="assets.length === 0" class="empty-state">
          Chưa có tài sản nào.
        </div>

        <div v-for="(asset, index) in assets" :key="'asset-'+index">
          <AssetForm
            :index="index"
            :asset="asset"
            :assetFields="assetFields"
            @update:asset="updateAsset(index, $event)"
            @remove="removeAsset(index)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import DynamicForm from '../components/DynamicForm.vue';
import PersonForm from '../components/PersonForm.vue';
import AssetForm from '../components/AssetForm.vue';

export default {
  name: 'LoanProfileForm',
  components: { DynamicForm, PersonForm, AssetForm },
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
      // Resize logic
      leftPanelWidth: 50, // Chia đều 50-50 để cân đối hơn
      isResizing: false,
      collapsedSections: {} // Lưu trạng thái collapse của từng section
    };
  },
  computed: {
    groupedFields() {
      return this.allFields.reduce((groups, field) => {
        const gName = field.group_name || 'Khác';
        const lowerGName = gName.toLowerCase();
        // Lọc bỏ Person + Asset khỏi phần chung
        if (lowerGName === 'thông tin cá nhân' || lowerGName === 'khach_hang' || lowerGName.includes('tài sản')) {
            return groups;
        }

        if (!groups[gName]) {
          groups[gName] = [];
        }
        groups[gName].push(field);
        return groups;
      }, {});
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
  mounted() {
    this.fetchFields();
    this.fetchRoles();
    if (this.id) {
      this.currentId = this.id;
      this.fetchProfileData(this.id);
    } else {
      this.addPerson();
      this.addAsset();
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
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/fields/');
        this.allFields = response.data;
      } catch (e) {
        console.error(e);
        alert('Lỗi tải cấu hình fields');
      } finally {
        this.loading = false;
      }
    },
    // Person Actions
    addPerson() {
      this.people.push({ id: null, ho_ten: '', cccd_so: '', roles: [], individual_field_values: {} });
    },
    removePerson(index) {
      if (confirm('Xóa người này?')) this.people.splice(index, 1);
    },
    updatePerson(index, updated) { this.people[index] = updated; },
    
    // Asset Actions
    addAsset() {
      this.assets.push({ id: null, asset_field_values: {} });
    },
    removeAsset(index) {
      if (confirm('Xóa tài sản này?')) this.assets.splice(index, 1);
    },
    updateAsset(index, updated) { this.assets[index] = updated; },

    async fetchProfileData(id) {
      try {
        this.loading = true;
        const response = await axios.get(`http://127.0.0.1:8000/api/loan-profiles/${id}/`);
        const data = response.data;
        this.profileName = data.name;
        this.generalFieldValues = data.field_values || {};
        this.people = data.people || [];
        this.assets = data.assets || []; // Load assets
        
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
          assets: this.assets // Gửi kèm assets
        };
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${targetId}/save_form_data/`, payload);
        alert('Lưu thành công!');
        this.$router.push('/');
      } catch (error) {
        console.error(error);
        alert('Lỗi khi lưu: ' + (error.response?.data?.message || error.message));
      } finally {
        this.isSaving = false;
      }
    }
  }
};
</script>

<style scoped>
.page-container { margin: 0 auto; padding: 20px; font-family: sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.form-layout { display: flex; user-select: none; /* Tránh bôi đen text khi kéo chuột */ }

/* Resize Handle Styles */
.resize-handle {
  width: 10px;
  background-color: #ddd;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}
.resize-handle:hover, .resize-handle:active {
  background-color: #42b983;
}
.handle-icon {
  font-size: 10px;
  color: #888;
  writing-mode: vertical-lr; /* Xoay chữ dọc */
}

/* Panels */
/* Lưu ý: width được set inline bởi Vue */
.left-panel { overflow-y: auto; padding-right: 15px; }
.right-panel { overflow-y: auto; padding-left: 15px; }

.panel-section { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #eee; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }

/* Collapsible Header Styles */
.section-header-row, .header-left { 
  display: flex; 
  align-items: center; 
  cursor: pointer; 
  user-select: none;
}
.header-left h3 { margin-right: 10px; }
.section-header-row h3 { flex-grow: 1; margin: 0; }

.toggle-icon {
  font-size: 12px;
  margin-left: 10px;
  transition: transform 0.2s;
  color: #666;
}
.toggle-icon.collapsed {
  transform: rotate(-90deg);
}

.panel-section h3, .panel-header h3 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid transparent; padding-bottom: 5px; display: inline-block; }
/* Add border only when not collapsed if needed, or keep simpler */
.panel-section h3 { border-bottom: 2px solid #42b983; } 
.panel-header h3 { border-bottom: 2px solid #42b983; }

.input-control { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.btn-primary { background: #42b983; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: #2c3e50; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
.empty-state { padding: 40px; text-align: center; background: #eee; color: #777; border-radius: 8px; border: 2px dashed #ccc; }
.field-group { margin-bottom: 15px; text-align: left; }
.field-group label { display: block; font-weight: bold; margin-bottom: 5px; }
</style>
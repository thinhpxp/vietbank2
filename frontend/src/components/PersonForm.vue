<template>
  <div class="person-card">
    <div class="card-header" @click="isCollapsed = !isCollapsed">
      <div class="header-left">
        <span class="toggle-icon" :class="{ 'collapsed': isCollapsed }">▼</span>
        <h4>{{ personLabel }} #{{ index + 1 }} <span v-if="displayName" class="person-name">- {{ displayName }}</span>
        </h4>
        <button v-if="!disabled" type="button" class="btn-search-master" @click.stop="isModalOpen = true"
          title="Chọn từ danh sách đã có">🔍</button>
      </div>
      <button v-if="!disabled" type="button" class="btn-remove" @click.stop="$emit('remove')">Xóa</button>
    </div>

    <div class="card-body" v-show="!isCollapsed">
      <!-- 2. Chọn Vai trò (Roles) -->
      <div class="roles-section">
        <label>Vai trò trong hồ sơ:</label>
        <div class="checkbox-group">
          <label v-for="role in availableRoles" :key="role" class="checkbox-inline">
            <input type="checkbox" :value="role" v-model="localPerson.roles" :disabled="disabled"> {{ role }}
          </label>
        </div>
      </div>

      <!-- 3. Các trường động của Người (Địa chỉ, SĐT...) -->
      <div class="dynamic-section" v-if="personFields.length > 0">
        <hr>
        <DynamicForm :fields="personFields" v-model="localPerson.individual_field_values" :disabled="disabled"
          :idPrefix="`person-${index}-`" @field-blur="handleFieldBlur" />
        <div v-if="duplicateWarning" class="alert-warning">
          <strong>⚠️ Cảnh báo:</strong> {{ duplicateWarning }}
        </div>
      </div>

      <!-- 4. Quản lý liên kết (Relations) -->
      <RelationManager 
        v-if="localPerson.master_object && localPerson.master_object.id"
        :masterObjectId="localPerson.master_object.id"
        :profileObjects="profileObjects"
        :currentObjectType="'PERSON'"
        :refreshTrigger="refreshTrigger"
        :allFields="allFields"
        :disabled="disabled"
      />
    </div>

    <ObjectSelectModal :isOpen="isModalOpen" type="person" @close="isModalOpen = false" @select="onPersonSelect" />
  </div>
</template>

<script>
import axios from 'axios';
import DynamicForm from './DynamicForm.vue';
import ObjectSelectModal from './ObjectSelectModal.vue';
import RelationManager from './RelationManager.vue';

export default {
  name: 'PersonForm',
  components: { DynamicForm, ObjectSelectModal, RelationManager },
  props: {
    index: Number,
    person: Object,
    personFields: Array,
    availableRoles: { type: Array, default: () => [] },
    availableTypes: { type: Array, default: () => [] },
    profileObjects: { type: Array, default: () => [] },
    // Full field definitions
    allFields: { type: Array, default: () => [] },
    disabled: { type: Boolean, default: false },
    refreshTrigger: { type: Number, default: 0 }
  },
  emits: ['update:person', 'remove'],
  data() {
    return {
      localPerson: JSON.parse(JSON.stringify(this.person)),
      isCollapsed: false,
      isModalOpen: false,
      duplicateWarning: null
    }
  },
  computed: {
    // Hiển thị tên hoặc CCCD khi collapse
    displayName() {
      const fv = this.localPerson.individual_field_values || {};
      const type = this.availableTypes.find(t => t.code === 'PERSON');

      if (type && type.identity_field_key) {
        return fv[type.identity_field_key] || '';
      }

      return fv.ho_ten || fv.cccd_so || '';
    },
    personLabel() {
      const type = this.availableTypes.find(t => t.code === 'PERSON');
      return type ? type.name : 'Người liên quan';
    }
  },
  watch: {
    localPerson: {
      handler(newVal) {
        this.$emit('update:person', newVal);
      },
      deep: true
    }
  },
  methods: {
    toggleCollapse() {
      this.isCollapsed = !this.isCollapsed;
    },
    onPersonSelect(person) {
      // 1. Link to Master Object
      this.localPerson.master_object = { id: person.id };

      // 2. Auto-fill all field values
      if (!this.localPerson.individual_field_values) {
        this.localPerson.individual_field_values = {};
      }

      // Copy all values from master (person.field_values contains the raw data)
      if (person.field_values) {
        this.localPerson.individual_field_values = {
          ...this.localPerson.individual_field_values,
          ...person.field_values
        };
      }

      this.$emit('update:person', this.localPerson);
      this.$toast.success(`Đã chọn: ${person.display_name}`);
    },
    async handleFieldBlur({ key, value }) {
      if (!value) {
        this.duplicateWarning = null;
        return;
      }

      // 1. Tìm cấu hình loại PERSON
      let typeConfig = this.availableTypes.find(t => t.code === 'PERSON');

      // Nếu chưa có cấu hình từ prop, thử tìm trong data nếu có (phòng hờ)
      if (!typeConfig) {
        console.warn('PersonForm: availableTypes empty or PERSON not found');
        return;
      }

      const idKey = typeConfig.identity_field_key || 'cccd'; // Fallback to 'cccd'
      if (idKey !== key) return;

      // 2. Nếu là trường định danh, gọi API kiểm tra
      try {
        const url = `http://127.0.0.1:8000/api/master-objects/check_identity/?object_type=PERSON&key=${key}&value=${encodeURIComponent(value)}`;
        const res = await axios.get(url);
        if (res.data.exists) {
          if (this.localPerson.master_object?.id === res.data.id) {
            this.duplicateWarning = null;
            return;
          }
          this.duplicateWarning = `Mã định danh '${value}' đã tồn tại trong Dữ liệu gốc (Đối tượng: ${res.data.display_name}). Khi lưu, hồ sơ sẽ tự động liên kết với dữ liệu đã có.`;
        } else {
          this.duplicateWarning = null;
        }
      } catch (error) {
        console.error('Lỗi kiểm tra định danh:', error);
      }
    }
  }
}
</script>

<style scoped>
.person-card {
  border: 1px solid #ddd;
  background: #fff;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  background: #efcebc;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ddd;
  cursor: pointer;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header h4 {
  margin: 0;
  color: #333;
}

.person-name {
  font-weight: normal;
  color: #555;
  font-size: 0.9em;
}

.card-body {
  padding: 15px;
}


.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.col {
  flex: 1;
  text-align: left;
}

.col label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.input-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.roles-section {
  text-align: left;
  margin-bottom: 15px;
}

.checkbox-inline {
  margin-right: 15px;
  cursor: pointer;
}


/* Toggle Icon */
.toggle-icon {
  font-size: 12px;
  transition: transform 0.2s;
  color: #666;
}

.toggle-icon.collapsed {
  transform: rotate(-90deg);
}

.alert-warning {
  background: #fffbe6;
  border: 1px solid #ffe58f;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  color: #856404;
  font-size: 0.9em;
  text-align: left;
}
</style>
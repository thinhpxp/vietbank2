<template>
  <div class="premium-card theme-person" :class="{ 'is-collapsed': isCollapsed }">
    <div class="card-header-glass" @click="isCollapsed = !isCollapsed">
      <div class="header-left">
        <SvgIcon name="chevron-down" size="xs" customClass="toggle-icon-svg" />
        <h4>{{ personLabel }} #{{ index + 1 }}</h4>
        <span v-if="displayName" class="person-name"> - {{ displayName }}</span>
      </div>
      <div class="header-actions">
        <button v-if="!disabled" type="button" class="btn-action btn-secondary btn-sm" @click.stop="isModalOpen = true"
          title="Chọn từ danh sách đã có">
          <SvgIcon name="search" size="xs" />
          <span>Tìm & Chọn</span>
        </button>
        <button v-if="!disabled" type="button" class="btn-remove-mini" @click.stop="$emit('remove')"
          title="Xóa người này">
          <SvgIcon name="trash" size="sm" />
        </button>
      </div>
    </div>

    <div class="card-body-content" v-show="!isCollapsed">
      <!-- 2. Chọn Vai trò (Roles) -->
      <div class="roles-section">
        <label class="font-bold mb-2 block">Vai trò trong hồ sơ:</label>
        <div class="flex gap-4 items-center flex-wrap">
          <label v-for="role in availableRoles" :key="role" class="admin-checkbox-label">
            <input type="checkbox" :value="role" v-model="localPerson.roles" :disabled="disabled">
            {{ role }}
          </label>
        </div>
      </div>

      <!-- 3. Các trường động của Người (Địa chỉ, SĐT...) -->
      <div class="dynamic-section mt-4" v-if="personFields.length > 0">
        <hr class="mb-4 opacity-10">
        <DynamicForm :fields="personFields" v-model="localPerson.individual_field_values" :disabled="disabled"
          :idPrefix="`person-${index}-`" :allSections="allSections" @field-blur="handleFieldBlur"
          @computed-update="$emit('computed-update', $event)" />
        <div v-if="duplicateWarning" class="alert-warning mt-4 clickable-warning" @click="linkDuplicate">
          <SvgIcon name="alert" size="sm" class="mr-2" />
          <span>{{ duplicateWarning }}</span>
        </div>
      </div>

      <!-- 4. Quản lý liên kết (Relations) -->
      <RelationManager v-if="isComplete"
        :masterObjectId="localPerson.master_object.id" :profileObjects="profileObjects" :currentObjectType="'PERSON'"
        :refreshTrigger="refreshTrigger" :allFields="allFields" :disabled="disabled" />
    </div>

    <ObjectSelectModal :isOpen="isModalOpen" type="person" @close="isModalOpen = false" @select="onPersonSelect" />
  </div>
</template>

<script>
import MasterService from '@/services/master.service';
import DynamicForm from './DynamicForm.vue';
import ObjectSelectModal from './ObjectSelectModal.vue';
import RelationManager from './RelationManager.vue';
import SvgIcon from './common/SvgIcon.vue';

export default {
  name: 'PersonForm',
  components: { DynamicForm, ObjectSelectModal, RelationManager, SvgIcon },
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
    refreshTrigger: { type: Number, default: 0 },
    allSections: { type: Object, default: () => ({}) }
  },
  emits: ['update:person', 'remove', 'computed-update'],
  data() {
    return {
      localPerson: JSON.parse(JSON.stringify(this.person)),
      isCollapsed: false,
      isModalOpen: false,
      duplicateWarning: null,
      duplicateId: null
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
    },
    isComplete() {
      if (!this.localPerson.master_object || !this.localPerson.master_object.id) return false;
      const type = this.availableTypes.find(t => t.code === 'PERSON');
      if (!type || !type.identity_field_key) return true;
      const fv = this.localPerson.individual_field_values || {};
      const idValue = fv[type.identity_field_key];
      return !!(idValue && (typeof idValue !== 'string' || idValue.trim() !== ''));
    }
  },
  watch: {
    localPerson: {
      handler(newVal) {
        this.$emit('update:person', newVal);
      },
      deep: true
    },
    person: {
      handler(newVal) {
        // Guard: Chỉ copy khi dữ liệu thực sự khác để tránh echo loop
        if (JSON.stringify(newVal) === JSON.stringify(this.localPerson)) return;
        this.localPerson = JSON.parse(JSON.stringify(newVal));
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
        const res = await MasterService.checkIdentity('PERSON', key, value);
        if (res.data.exists) {
          if (this.localPerson.master_object?.id === res.data.id) {
            this.duplicateWarning = null;
            return;
          }
          this.duplicateWarning = ` Mã định danh '${value}' đã tồn tại trong Dữ liệu gốc: "${res.data.display_name}". Bấm để chọn thay vì tạo mới.`;
          this.duplicateId = res.data.id;
          if (!this.localPerson.master_object) this.localPerson.master_object = {};
          this.localPerson.master_object._duplicateMasterId = res.data.id;
          this.localPerson.master_object._duplicateDisplayName = res.data.display_name;
          this.localPerson.master_object._duplicateValue = value;
        } else {
          this.duplicateWarning = null;
          this.duplicateId = null;
          if (this.localPerson.master_object) {
            delete this.localPerson.master_object._duplicateMasterId;
            delete this.localPerson.master_object._duplicateDisplayName;
            delete this.localPerson.master_object._duplicateValue;
          }
        }
      } catch (error) {
        console.error('Lỗi kiểm tra định danh:', error);
      }
    },
    async linkDuplicate() {
      if (!this.duplicateId) return;
      try {
        const res = await MasterService.getObjectById(this.duplicateId);
        this.onPersonSelect(res.data);
        this.duplicateWarning = null;
        this.duplicateId = null;
      } catch (error) {
        console.error('Lỗi khi liên kết đối tượng trùng:', error);
      }
    }
  }
}
</script>

<style scoped>
.person-name {
  font-weight: normal;
  color: var(--slate-500);
  font-size: 0.9em;
  font-style: italic;
}

.roles-section {
  background: var(--slate-50);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  text-align: left;
}

.alert-warning {
  background: #efc83d;
  border: 1px solid #060606;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  color: var(--color-warning-text);
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  transition: all 0.2s;
}

.clickable-warning {
  cursor: pointer;
}

.clickable-warning:hover {
  background: white;
  border-color: var(--color-warning-text);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.opacity-10 {
  opacity: 0.1;
}

.block {
  display: block;
}

.mt-4 {
  margin-top: var(--spacing-lg);
}
</style>

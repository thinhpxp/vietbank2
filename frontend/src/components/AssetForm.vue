<template>
  <div class="premium-card theme-asset" :class="{ 'is-collapsed': isCollapsed }">
    <div class="card-header-glass" @click="isCollapsed = !isCollapsed">
      <div class="header-left">
        <SvgIcon name="chevron-down" size="xs" customClass="toggle-icon-svg" />
        <h4>{{ objectLabel }} #{{ index + 1 }}</h4>
        <span v-if="displayInfo" class="asset-info"> - {{ displayInfo }}</span>
      </div>
      <div class="header-actions">
        <button v-if="!disabled" type="button" class="btn-action btn-secondary btn-sm" @click.stop="isModalOpen = true"
          title="Chọn từ danh sách đã có">
          <SvgIcon name="search" size="xs" />
          <span>Tìm & Chọn</span>
        </button>
        <button v-if="!disabled" class="btn-remove-mini" @click.stop="$emit('remove')" title="Xóa tài sản này">
          <SvgIcon name="trash" size="sm" />
        </button>
      </div>
    </div>

    <div v-show="!isCollapsed" class="card-body-content">
      <!-- Type Selector -->
      <div class="type-selector-premium mb-4">
        <label class="font-bold mb-2 block">Phân loại đối tượng:</label>
        <div class="flex gap-2">
          <select v-model="selectedType" class="admin-select" @change="onTypeChange" :disabled="disabled">
            <option :value="null">-- Chọn phân loại --</option>
            <option v-for="type in assetTypes" :key="type.code" :value="type.code">
              {{ type.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="dynamic-section mt-4" v-if="selectedType">
        <hr class="mb-4 opacity-10">
        <DynamicForm :fields="filteredAssetFields" :modelValue="localAsset.individual_field_values" :disabled="disabled"
          :idPrefix="`asset-${index}-`" :allSections="allSections" @update:modelValue="onUpdateValues"
          @field-blur="handleFieldBlur" @computed-update="$emit('computed-update', $event)" />
        <div v-if="duplicateWarning" class="alert-warning mt-4">
          <SvgIcon name="alert" size="sm" class="mr-2" />
          <span>{{ duplicateWarning }}</span>
        </div>
      </div>

      <div v-else class="empty-state-standard">
        Vui lòng chọn <strong>Phân loại đối tượng</strong> để nhập thông tin chi tiết.
      </div>

      <!-- Quản lý liên kết (Relations) -->
      <RelationManager v-if="localAsset.master_object && localAsset.master_object.id"
        :masterObjectId="localAsset.master_object.id" :profileObjects="profileObjects" :currentObjectType="selectedType"
        :refreshTrigger="refreshTrigger" :allFields="allFields" :disabled="disabled" />
    </div>

    <ObjectSelectModal :isOpen="isModalOpen" type="asset" @close="isModalOpen = false" @select="onAssetSelect" />
  </div>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import DynamicForm from './DynamicForm.vue';
import ObjectSelectModal from './ObjectSelectModal.vue';
import RelationManager from './RelationManager.vue';
import SvgIcon from './common/SvgIcon.vue';

export default {
  name: 'AssetForm',
  components: { DynamicForm, ObjectSelectModal, RelationManager, SvgIcon },
  props: {
    index: { type: Number, required: true },
    asset: { type: Object, required: true },
    assetFields: { type: Array, default: () => [] },
    availableTypes: { type: Array, default: () => [] },
    profileObjects: { type: Array, default: () => [] },
    // Full field definitions for detail modal
    allFields: { type: Array, default: () => [] },
    disabled: { type: Boolean, default: false },
    refreshTrigger: { type: Number, default: 0 },
    allSections: { type: Object, default: () => ({}) }
  },
  emits: ['update:asset', 'remove', 'computed-update'],
  data() {
    return {
      localAsset: {
        ...JSON.parse(JSON.stringify(this.asset)),
        individual_field_values: this.asset.individual_field_values || this.asset.asset_field_values || {},
        roles: this.asset.roles || []
      },
      isCollapsed: false,
      isModalOpen: false,
      assetTypes: [],
      selectedType: this.asset.master_object?.object_type || null,
      duplicateWarning: null
    };
  },
  computed: {
    // Hiển thị một thông tin tóm tắt khi collapse
    displayInfo() {
      const fv = this.localAsset.individual_field_values || {};
      const type = this.assetTypes.find(t => t.code === this.selectedType);

      if (type && type.identity_field_key) {
        return fv[type.identity_field_key] || '';
      }

      return fv.ten_tai_san || fv.loai_tai_san || '';
    },
    // Filter fields based on selected Object Type
    filteredAssetFields() {
      if (!this.selectedType) return [];
      return this.assetFields.filter(f => {
        const groupAllowed = f.group_allowed_object_type_codes || [];
        const fieldAllowed = f.allowed_object_type_codes || [];

        // Logic ưu tiên:
        // 1. Nếu FIELD có định nghĩa loại cụ thể -> Chỉ theo FIELD
        if (fieldAllowed.length > 0) {
          return fieldAllowed.includes(this.selectedType);
        }

        // 2. Nếu FIELD không có nhưng GROUP có -> Theo GROUP
        if (groupAllowed.length > 0) {
          return groupAllowed.includes(this.selectedType);
        }

        // 3. Nếu cả hai đều trống -> Cho phép tất cả (Trường thông tin chung)
        return true;
      });
    },
    objectLabel() {
      if (!this.selectedType) return 'Đối tượng';
      const type = this.assetTypes.find(t => t.code === this.selectedType);
      if (!type) return 'Đối tượng';

      const fv = this.localAsset.individual_field_values || {};
      if (type.identity_field_key && fv[type.identity_field_key]) {
        return `${type.name}: ${fv[type.identity_field_key]}`;
      }

      return type.name;
    }
  },
  watch: {
    asset: {
      handler(newVal) {
        // Guard: Chỉ copy khi dữ liệu thực sự khác để tránh echo loop
        const newStr = JSON.stringify(newVal);
        const oldStr = JSON.stringify(this.localAsset);
        if (newStr === oldStr) return;
        this.localAsset = {
          ...JSON.parse(JSON.stringify(newVal)),
          individual_field_values: newVal.individual_field_values || newVal.asset_field_values || {}
        };
        this.selectedType = newVal.master_object?.object_type || null;
      },
      deep: true
    }
  },
  async mounted() {
    // We use the availableTypes prop which should be passed from LoanProfileForm
    if (this.availableTypes && this.availableTypes.length > 0) {
      this.assetTypes = this.availableTypes.filter(t => t.code !== 'PERSON');
    } else {
      await this.fetchAssetTypes();
    }
  },
  methods: {
    getObjectTypeId(code) {
      const type = this.availableTypes.find(t => t.code === code);
      return type ? type.id : null;
    },
    async fetchAssetTypes() {
      if (this.availableTypes && this.availableTypes.length > 0) {
        this.assetTypes = this.availableTypes.filter(t => t.code !== 'PERSON');
        return;
      }
      try {
        const res = await axios.get(`${API_URL}/object-types/`);
        // Filter only asset-related types (exclude PERSON)
        this.assetTypes = res.data.filter(t => t.code !== 'PERSON');
      } catch (e) {
        console.error('Lỗi tải loại tài sản:', e);
      }
    },
    onTypeChange() {
      this.localAsset.master_object = {
        ...this.localAsset.master_object,
        object_type: this.selectedType
      };
      this.$emit('update:asset', this.localAsset);
    },
    onUpdateValues(newValues) {
      this.localAsset.individual_field_values = newValues;
      this.$emit('update:asset', this.localAsset);
    },
    onAssetSelect(asset) {
      this.localAsset.master_object = {
        id: asset.id,
        object_type: asset.object_type
      };
      this.selectedType = asset.object_type;

      if (!this.localAsset.individual_field_values) {
        this.localAsset.individual_field_values = {};
      }

      if (asset.field_values) {
        this.localAsset.individual_field_values = {
          ...this.localAsset.individual_field_values,
          ...asset.field_values
        };
      }

      this.$emit('update:asset', this.localAsset);
    },
    async handleFieldBlur({ key, value }) {
      if (!value || !this.selectedType) {
        this.duplicateWarning = null;
        return;
      }

      // 1. Kiểm tra xem đây có phải trường định danh không
      const typeConfig = this.assetTypes.find(t => t.code === this.selectedType);
      if (!typeConfig) return;

      const idKey = typeConfig.identity_field_key;
      if (idKey !== key) return;

      // 2. Nếu là trường định danh, gọi API kiểm tra
      try {
        const url = `${API_URL}/master-objects/check_identity/?object_type=${this.selectedType}&key=${key}&value=${encodeURIComponent(value)}`;
        const res = await axios.get(url);
        if (res.data.exists) {
          if (this.localAsset.master_object?.id === res.data.id) {
            this.duplicateWarning = null;
            return;
          }
          this.duplicateWarning = `Tài sản có mã '${value}' đã tồn tại trong Dữ liệu gốc (Đối tượng: ${res.data.display_name}). Khi lưu, hồ sơ sẽ tự động liên kết với dữ liệu đã có.`;
        } else {
          this.duplicateWarning = null;
        }
      } catch (error) {
        console.error('Lỗi kiểm tra định danh tài sản:', error);
      }
    }
  }
}
</script>

<style scoped>
.asset-info {
  font-weight: normal;
  color: var(--slate-500);
  font-size: 0.9em;
  font-style: italic;
}

.type-selector-premium {
  background: var(--slate-50);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border-bottom: 2px solid var(--color-success);
}

.alert-warning {
  background: #fffbe6;
  border: 1px solid #ffe58f;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  color: #856404;
  font-size: 0.9em;
  display: flex;
  align-items: center;
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

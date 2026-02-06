<template>
  <div class="asset-card">
    <div class="card-header" @click="isCollapsed = !isCollapsed">
      <div class="header-left">
        <span class="toggle-icon" :class="{ 'collapsed': isCollapsed }">▼</span>
        <h4>{{ objectLabel }} #{{ index + 1 }} <span v-if="displayInfo" class="asset-info">- {{ displayInfo }}</span>
        </h4>
        <button v-if="!disabled" type="button" class="btn-search-master" @click.stop="isModalOpen = true"
          title="Chọn từ danh sách đã có">🔍</button>
      </div>
      <button v-if="!disabled" class="btn-remove" @click.stop="$emit('remove')">Xóa</button>
    </div>

    <div v-if="!isCollapsed" class="card-body">
      <!-- Type Selector -->
      <div class="type-selector-row">
        <label class="type-label">Phân loại đối tượng:</label>
        <select v-model="selectedType" class="type-dropdown" @change="onTypeChange" :disabled="disabled">
          <option :value="null">-- Chọn phân loại --</option>
          <option v-for="type in assetTypes" :key="type.code" :value="type.code">
            {{ type.name }}
          </option>
        </select>
      </div>

      <DynamicForm :fields="filteredAssetFields" :modelValue="localAsset.individual_field_values" :disabled="disabled"
        :idPrefix="`asset-${index}-`" @update:modelValue="onUpdateValues" @field-blur="handleFieldBlur" />
      <div v-if="duplicateWarning" class="alert-warning">
        <strong>⚠️ Cảnh báo:</strong> {{ duplicateWarning }}
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

export default {
  name: 'AssetForm',
  components: { DynamicForm, ObjectSelectModal, RelationManager },
  props: {
    index: { type: Number, required: true },
    asset: { type: Object, required: true },
    assetFields: { type: Array, default: () => [] },
    availableTypes: { type: Array, default: () => [] },
    profileObjects: { type: Array, default: () => [] },
    // Full field definitions for detail modal
    allFields: { type: Array, default: () => [] },
    disabled: { type: Boolean, default: false },
    refreshTrigger: { type: Number, default: 0 }
  },
  emits: ['update:asset', 'remove'],
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
        this.localAsset = {
          ...JSON.parse(JSON.stringify(newVal)),
          individual_field_values: newVal.individual_field_values || newVal.asset_field_values || {}
        };
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
.asset-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 20px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.type-selector-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f0f8ff;
  border-radius: 8px;
  border: 2px solid #42b983;
}

.type-label {
  font-weight: bold;
  color: #2c3e50;
  white-space: nowrap;
}

.type-dropdown {
  flex: 1;
  padding: 8px 12px;
  font-size: 1rem;
  border: 2px solid #42b983;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.type-dropdown:focus {
  outline: none;
  border-color: #369870;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #fdf6e3;
  border-bottom: 1px solid #eee;
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
  color: #e67e22;
}

.asset-info {
  font-weight: normal;
  color: #888;
  font-size: 0.9em;
}


.card-body {
  padding: 15px;
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

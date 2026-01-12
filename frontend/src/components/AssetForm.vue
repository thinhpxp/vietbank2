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

      <DynamicForm :fields="filteredAssetFields" :modelValue="asset.asset_field_values"
        :disabled="disabled" @update:modelValue="onUpdateValues" @field-blur="handleFieldBlur" />
      <div v-if="duplicateWarning" class="alert-warning">
        <strong>⚠️ Cảnh báo:</strong> {{ duplicateWarning }}
      </div>
    </div>

    <ObjectSelectModal :isOpen="isModalOpen" type="asset" @close="isModalOpen = false" @select="onAssetSelect" />
  </div>
</template>

<script>
import axios from 'axios';
import DynamicForm from './DynamicForm.vue';
import ObjectSelectModal from './ObjectSelectModal.vue';

export default {
  name: 'AssetForm',
  components: { DynamicForm, ObjectSelectModal },
  props: {
    index: { type: Number, required: true },
    asset: { type: Object, required: true },
    assetFields: { type: Array, default: () => [] },
    availableTypes: { type: Array, default: () => [] },
    disabled: { type: Boolean, default: false }
  },
  emits: ['update:asset', 'remove'],
  data() {
    return {
      localAssetData: { ...this.asset },
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
      const fv = this.localAssetData.asset_field_values || {};
      const type = this.assetTypes.find(t => t.code === this.selectedType);

      // Nếu có cấu hình identity_field_key, dùng nó làm info chính
      if (type && type.identity_field_key) {
        return fv[type.identity_field_key] || '';
      }

      // Fallback
      return fv.ten_tai_san || fv.loai_tai_san || '';
    },
    // Filter fields based on selected Object Type
    filteredAssetFields() {
      if (!this.selectedType) return []; // If no type selected, show no fields or a default set
      return this.assetFields.filter(f => {
        const allowed = f.allowed_object_types || [];
        // If allowed_object_types is empty, it means the field is allowed for all types.
        // Otherwise, check if the current selected type's ID is in the allowed list.
        return allowed.length === 0 || allowed.includes(this.typeIdMap[this.selectedType]);
      });
    },
    objectLabel() {
      if (!this.selectedType) return 'Đối tượng';
      const type = this.assetTypes.find(t => t.code === this.selectedType);
      if (!type) return 'Đối tượng';

      const fv = this.localAssetData.asset_field_values || {};
      // Nếu có giá trị của trường định danh, hiển thị "Loại: Giá trị"
      if (type.identity_field_key && fv[type.identity_field_key]) {
        return `${type.name}: ${fv[type.identity_field_key]}`;
      }

      return type.name;
    },
    typeIdMap() {
      return this.assetTypes.reduce((map, t) => {
        map[t.code] = t.id;
        return map;
      }, {});
    }
  },
  watch: {
    asset: {
      handler(newVal) {
        this.localAssetData = { ...newVal };
      },
      deep: true
    }
  },
  async mounted() {
    await this.fetchAssetTypes();
  },
  methods: {
    getObjectTypeId(code) {
      // Helper to find ID from Code. We need access to master types.
      // pass master types as props or fetch?
      // Simplest: The asset object should have the ID if possible, but currently we rely on code.
      // Let's assume we pass availableTypes as prop or store.
      // Quick fix: Map code to ID using availableTypes prop
      const type = this.availableTypes.find(t => t.code === code);
      return type ? type.id : null;
    },
    async fetchAssetTypes() {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/object-types/');
        // Filter only asset-related types (exclude PERSON)
        this.assetTypes = res.data.filter(t => t.code !== 'PERSON');
      } catch (e) {
        console.error('Lỗi tải loại tài sản:', e);
      }
    },
    onTypeChange() {
      // Update the asset object structure
      this.localAssetData.master_object = {
        object_type: this.selectedType
      };
      this.$emit('update:asset', this.localAssetData);
    },
    onUpdateValues(newValues) {
      this.localAssetData.asset_field_values = newValues;
      this.$emit('update:asset', this.localAssetData);
    },
    onAssetSelect(asset) {
      // 1. Link to Master Object & Type
      this.localAssetData.master_object = {
        id: asset.id,
        object_type: asset.object_type
      };
      this.selectedType = asset.object_type;

      // 2. Auto-fill all field values
      if (!this.localAssetData.asset_field_values) {
        this.localAssetData.asset_field_values = {};
      }

      if (asset.field_values) {
        this.localAssetData.asset_field_values = {
          ...this.localAssetData.asset_field_values,
          ...asset.field_values
        };
      }

      this.$emit('update:asset', this.localAssetData);
      alert(`Đã chọn tài sản: ${asset.display_name}`);
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
        const url = `http://127.0.0.1:8000/api/master-objects/check_identity/?object_type=${this.selectedType}&key=${key}&value=${encodeURIComponent(value)}`;
        const res = await axios.get(url);
        if (res.data.exists) {
          // Nếu đã tồn tại nhưng chính là vật này thì bỏ qua
          if (this.localAssetData.master_object?.id === res.data.id) {
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

.btn-search-master {
  background: #e67e22;
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-left: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-search-master:hover {
  background: #d35400;
}

.card-body {
  padding: 15px;
}

.btn-remove {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
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

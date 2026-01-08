<template>
  <div class="asset-card">
    <div class="card-header" @click="isCollapsed = !isCollapsed">
      <div class="header-left">
        <span class="toggle-icon" :class="{ 'collapsed': isCollapsed }">▼</span>
        <h4>Tài sản BĐ #{{ index + 1 }} <span v-if="displayInfo" class="asset-info">- {{ displayInfo }}</span></h4>
        <button type="button" class="btn-search-master" @click.stop="isModalOpen = true"
          title="Chọn từ danh sách đã có">🔍</button>
      </div>
      <button class="btn-remove" @click.stop="$emit('remove')">Xóa</button>
    </div>

    <div class="card-body" v-show="!isCollapsed">
      <DynamicForm :fields="assetFields" :modelValue="localAssetData.asset_field_values"
        @update:modelValue="onUpdateFieldValues" />
    </div>

    <ObjectSelectModal :isOpen="isModalOpen" type="asset" @close="isModalOpen = false" @select="onAssetSelect" />
  </div>
</template>

<script>
import DynamicForm from './DynamicForm.vue';
import ObjectSelectModal from './ObjectSelectModal.vue';

export default {
  name: 'AssetForm',
  components: { DynamicForm, ObjectSelectModal },
  props: {
    index: { type: Number, required: true },
    asset: { type: Object, required: true },
    assetFields: { type: Array, default: () => [] }
  },
  emits: ['update:asset', 'remove'],
  data() {
    return {
      localAssetData: { ...this.asset },
      isCollapsed: false,
      isModalOpen: false
    };
  },
  computed: {
    // Hiển thị một thông tin tóm tắt khi collapse
    displayInfo() {
      const fv = this.localAssetData.asset_field_values || {};
      // Thử lấy một key tiêu biểu (ví dụ: ten_tai_san hoặc loai_tai_san)
      return fv.ten_tai_san || fv.loai_tai_san || '';
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
  methods: {
    onUpdateFieldValues(newValues) {
      this.localAssetData.asset_field_values = newValues;
      this.$emit('update:asset', this.localAssetData);
    },
    onAssetSelect(asset) {
      if (!this.localAssetData.asset_field_values) {
        this.localAssetData.asset_field_values = {};
      }

      // Auto-fill thông tin từ master
      if (asset.so_giay_chung_nhan) {
        this.localAssetData.asset_field_values.so_giay_chung_nhan = asset.so_giay_chung_nhan;
      }

      alert(`Đã chọn tài sản: ${asset.so_giay_chung_nhan}`);
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
</style>

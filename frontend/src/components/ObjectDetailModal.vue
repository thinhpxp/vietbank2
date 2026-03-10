<template>
  <BaseModal :isOpen="!!objectId" :title="$t('CHI_TIET_DOI_TUONG')" @close="$emit('close')">
    <div v-if="loading" class="text-center p-4">
      <div class="loading-spinner"></div>
      <p>Đang tải dữ liệu...</p>
    </div>

    <div v-else-if="error" class="text-center text-red-500 p-4">
      {{ error }}
    </div>

    <div v-else-if="objectData" class="admin-form-section">
      <!-- Section: Thông tin chung -->
      <div class="mb-6">
        <h4 class="text-sm font-bold text-gray-700 uppercase mb-3 border-b pb-1 flex items-center gap-2">
          <span>📋</span> {{ $t('THONG_TIN_CHUNG') }}
        </h4>
        <div class="data-table-vxe">
          <vxe-table border round :data="generalInfoList" :show-header="false" :column-config="{ resizable: true }">
            <vxe-column field="label" width="150">
              <template #default="{ row }">
                <span class="font-medium text-gray-600">{{ row.label }}</span>
              </template>
            </vxe-column>
            <vxe-column field="value">
              <template #default="{ row }">
                <span v-if="row.key === 'LOAI_DOI_TUONG'" class="badge badge-custom">{{ row.value }}</span>
                <span v-else class="font-bold break-all">{{ row.value }}</span>
              </template>
            </vxe-column>
          </vxe-table>
        </div>
      </div>

      <!-- Section: Chi tiết thuộc tính -->
      <div>
        <h4 class="text-sm font-bold text-gray-700 uppercase mb-3 border-b pb-1 flex items-center gap-2">
          <span>🔍</span> {{ $t('THUOC_TINH_CHI_TIET') }}
        </h4>
        <div class="data-table-vxe">
          <vxe-table border round :data="attributeList" :column-config="{ resizable: true }"
            :row-config="{ isHover: true }">
            <vxe-column field="label" :title="$t('TRUONG_DU_LIEU')" width="150"></vxe-column>
            <vxe-column field="value" :title="$t('GIA_TRI')">
              <template #default="{ row }">
                <div class="break-all">{{ row.value }}</div>
              </template>
            </vxe-column>
            <template #empty>
              <div class="py-6 text-center text-gray-400 italic">
                {{ $t('KHONG_CO_DU_LIEU_CHI_TIET') }}
              </div>
            </template>
          </vxe-table>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn-action btn-secondary" @click="$emit('close')">
        {{ $t('DONG') }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import MasterService from '@/services/master.service';
import BaseModal from './BaseModal.vue';

export default {
  name: 'ObjectDetailModal',
  components: { BaseModal },
  props: {
    objectId: {
      type: [Number, String],
      default: null
    },
    // Nhận danh sách định nghĩa trường để hiển thị Label thay vì Key
    fieldDefinitions: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      objectData: null
    };
  },
  computed: {
    fieldValues() {
      if (!this.objectData || !this.objectData.field_values) return {};

      const rawValues = this.objectData.field_values;
      const objectType = this.objectData.object_type;
      const filtered = {};

      // Chỉ lấy các giá trị mà field definition cho phép loại đối tượng này
      Object.keys(rawValues).forEach(key => {
        const fieldDef = this.fieldDefinitions.find(f => f.placeholder_key === key);

        // Nếu không tìm thấy định nghĩa, hiển thị mặc định (để tránh mất dữ liệu quan trọng)
        if (!fieldDef) {
          filtered[key] = rawValues[key];
          return;
        }

        // Danh sách các loại đối tượng được phép từ cả Nhóm và Trường (Dùng mã Code)
        const groupAllowed = fieldDef.group_allowed_object_type_codes || [];
        const fieldAllowed = fieldDef.allowed_object_type_codes || [];

        // Logic ưu tiên:
        // 1. Nếu FIELD có định nghĩa loại cụ thể -> Chỉ theo FIELD
        if (fieldAllowed.length > 0) {
          if (fieldAllowed.includes(objectType)) {
            filtered[key] = rawValues[key];
          }
          return;
        }

        // 2. Nếu FIELD không có nhưng GROUP có -> Theo GROUP
        if (groupAllowed.length > 0) {
          if (groupAllowed.includes(objectType)) {
            filtered[key] = rawValues[key];
          }
          return;
        }

        // 3. Nếu cả hai đều trống -> Cho phép tất cả (thông tin chung)
        filtered[key] = rawValues[key];
      });

      return filtered;
    },
    generalInfoList() {
      if (!this.objectData) return [];
      return [
        { key: 'LOAI_DOI_TUONG', label: this.$t('LOAI_DOI_TUONG'), value: this.objectData.object_type_display },
        { key: 'TEN_HIEN_THI', label: this.$t('TEN_HIEN_THI'), value: this.objectData.display_name }
      ];
    },
    attributeList() {
      return Object.entries(this.fieldValues).map(([key, value]) => ({
        key,
        label: this.getLabel(key),
        value
      }));
    }
  },
  watch: {
    objectId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchObjectDetails(newVal);
        } else {
          this.objectData = null;
          this.error = null;
        }
      }
    }
  },
  methods: {
    async fetchObjectDetails(id) {
      this.loading = true;
      this.error = null;
      this.objectData = null;
      try {
        const response = await MasterService.getObjectById(id);
        this.objectData = response.data;
      } catch (err) {
        console.error("Lỗi tải chi tiết đối tượng:", err);
        this.error = this.$t('LOI_TAI_DU_LIEU');
      } finally {
        this.loading = false;
      }
    },
    getLabel(key) {
      // 1. Tìm trong định nghĩa trường (ưu tiên cao nhất)
      if (this.fieldDefinitions && this.fieldDefinitions.length > 0) {
        const field = this.fieldDefinitions.find(f => f.placeholder_key === key);
        if (field) return field.label;
      }

      // 2. Nếu không có định nghĩa, thử dịch bằng dictionary (dành cho các key hệ thống như HDTC)
      const translated = this.$t(key);
      if (translated && translated !== key) return translated;

      // 3. Fallback: Trả về key gốc
      return key;
    }
  }
};
</script>

<style scoped>
/* Spinner cho loading state */
.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>

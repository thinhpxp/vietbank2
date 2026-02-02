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
      <div class="mb-4">
        <h4 class="text-sm font-bold text-gray-700 uppercase mb-2 border-b pb-1">
          {{ $t('THONG_TIN_CHUNG') }}
        </h4>
        <table class="admin-table w-full mb-4">
          <tbody>
            <tr class="border-b last:border-0 hover:bg-gray-50">
              <td class="py-2 px-3 text-sm text-gray-600 font-medium w-1/3">
                {{ $t('LOAI_DOI_TUONG') }}
              </td>
              <td class="py-2 px-3 text-sm font-bold text-gray-800">
                {{ objectData.object_type_display }}
              </td>
            </tr>
            <tr class="border-b last:border-0 hover:bg-gray-50">
              <td class="py-2 px-3 text-sm text-gray-600 font-medium w-1/3">
                {{ $t('TEN_HIEN_THI') }}
              </td>
              <td class="py-2 px-3 text-sm font-bold text-gray-800 break-words">
                {{ objectData.display_name }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Section: Chi tiết thuộc tính -->
      <div>
        <h4 class="text-sm font-bold text-gray-700 uppercase mb-2 border-b pb-1">
          {{ $t('THUO_TINH_CHI_TIET') }}
        </h4>
        <table class="admin-table w-full">
          <thead>
            <tr>
              <th class="text-left py-2 px-3 bg-gray-50 text-xs font-semibold text-gray-600">
                {{ $t('TRUONG_DU_LIEU') }}
              </th>
              <th class="text-left py-2 px-3 bg-gray-50 text-xs font-semibold text-gray-600">
                {{ $t('GIA_TRI') }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(value, key) in fieldValues" :key="key" class="border-b last:border-0 hover:bg-gray-50">
              <td class="py-2 px-3 text-sm text-gray-600 font-medium w-1/3">
                {{ getLabel(key) }}
                <!-- <div class="text-xs text-gray-400 font-normal">{{ key }}</div> -->
              </td>
              <td class="py-2 px-3 text-sm text-gray-800">
                {{ value }}
              </td>
            </tr>
            <tr v-if="Object.keys(fieldValues).length === 0">
              <td colspan="2" class="py-4 text-center text-gray-500 text-sm italic">
                {{ $t('KHONG_CO_DU_LIEU_CHI_TIET') }}
              </td>
            </tr>
          </tbody>
        </table>
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
import axios from 'axios';
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
      // Trả về object chứa các giá trị field
      return this.objectData ? (this.objectData.field_values || {}) : {};
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
        const response = await axios.get(`http://127.0.0.1:8000/api/master-objects/${id}/`);
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

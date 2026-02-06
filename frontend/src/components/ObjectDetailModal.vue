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
        <div class="ui-table-wrapper">
          <table class="data-table allow-wrap w-full">
            <tbody>
              <tr>
                <td class="font-medium text-gray-600 w-1/3">{{ $t('LOAI_DOI_TUONG') }}</td>
                <td>
                  <span class="badge badge-custom">{{ objectData.object_type_display }}</span>
                </td>
              </tr>
              <tr>
                <td class="font-medium text-gray-600">{{ $t('TEN_HIEN_THI') }}</td>
                <td class="font-bold break-all">{{ objectData.display_name }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section: Chi tiết thuộc tính -->
      <div>
        <h4 class="text-sm font-bold text-gray-700 uppercase mb-3 border-b pb-1 flex items-center gap-2">
          <span>🔍</span> {{ $t('THUO_TINH_CHI_TIET') }}
        </h4>
        <div class="ui-table-wrapper">
          <table class="data-table allow-wrap w-full">
            <thead>
              <tr>
                <th class="w-1/3">{{ $t('TRUONG_DU_LIEU') }}</th>
                <th>{{ $t('GIA_TRI') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(value, key) in fieldValues" :key="key">
                <td class="font-medium text-gray-600">{{ getLabel(key) }}</td>
                <td class="break-all">{{ value }}</td>
              </tr>
              <tr v-if="Object.keys(fieldValues).length === 0">
                <td colspan="2" class="py-6 text-center text-gray-400 italic">
                  {{ $t('KHONG_CO_DU_LIEU_CHI_TIET') }}
                </td>
              </tr>
            </tbody>
          </table>
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
import axios from 'axios';
import { API_URL } from '@/store/auth';
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
        const response = await axios.get(`${API_URL}/master-objects/${id}/`);
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

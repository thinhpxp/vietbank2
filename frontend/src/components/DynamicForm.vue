<template>
  <div class="dynamic-inputs">
    <div v-for="field in sortedFields" :key="field.id" class="form-field"
      :style="{ gridColumn: `span ${field.width_cols || 12}` }" :class="field.css_class">
      <label :for="field.placeholder_key">{{ field.label }}</label>

      <!-- Text Input -->
      <div v-if="field.data_type === 'TEXT'" class="input-with-tools">
        <input type="text" :id="field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)" class="input-control" />
        <button v-if="hasDynamicTemplate(field)" class="btn-magic" title="Tự động điền theo mẫu"
          @click="applyTemplate(field)">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 4V2m0 12v-2M8 8V6m0 12v-2M3 21l6-6m-4 4l5-5m1.5-1.5L21 3m-9 9l4.5-4.5" />
          </svg>
        </button>
      </div>

      <!-- Textarea Input (MỚI) -->
      <div v-else-if="field.data_type === 'TEXTAREA'" class="input-with-tools">
        <textarea :id="field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)" class="input-control custom-textarea"
          rows="4"></textarea>
        <button v-if="hasDynamicTemplate(field)" class="btn-magic" title="Tự động điền theo mẫu"
          @click="applyTemplate(field)">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 4V2m0 12v-2M8 8V6m0 12v-2M3 21l6-6m-4 4l5-5m1.5-1.5L21 3m-9 9l4.5-4.5" />
          </svg>
        </button>
      </div>

      <!-- Number Input -->
      <template v-else-if="field.data_type === 'NUMBER'">
        <!-- Nếu bật phân tách hàng nghìn: Dùng text input để format linh hoạt -->
        <input v-if="field.use_digit_grouping" type="text" :id="field.placeholder_key"
          :value="formatNumber(modelValue[field.placeholder_key])"
          @input="handleNumberInput(field.placeholder_key, $event.target.value)" class="input-control"
          placeholder="0" />
        <!-- Nếu không: Dùng number input truyền thống -->
        <input v-else type="number" :id="field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)" class="input-control" />
      </template>

      <!-- Date Input (Option 2: Hybrid Text + Date Picker) -->
      <div v-else-if="field.data_type === 'DATE'" class="date-input-wrapper">
        <input type="text" :id="field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)" class="input-control hybrid-text"
          placeholder="Ngày/Tháng/Năm" />
        <div class="calendar-trigger" @click="openPicker(field.placeholder_key)">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <input type="date" class="hidden-picker" :ref="'picker_' + field.placeholder_key"
            @change="handlePickerChange(field.placeholder_key, $event.target.value)" />
        </div>
      </div>

      <!-- Checkbox -->
      <div v-else-if="field.data_type === 'CHECKBOX'">
        <input type="checkbox" :id="field.placeholder_key"
          :checked="modelValue[field.placeholder_key] === 'true' || modelValue[field.placeholder_key] === true"
          @change="updateValue(field.placeholder_key, $event.target.checked)" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DynamicForm',
  props: {
    fields: { type: Array, required: true },
    modelValue: { type: Object, required: true }
  },
  emits: ['update:modelValue'],
  computed: {
    sortedFields() {
      // Sắp xếp fields theo order tăng dần
      return [...this.fields].sort((a, b) => (a.order || 0) - (b.order || 0));
    }
  },
  methods: {
    updateValue(key, value) {
      const newData = { ...this.modelValue, [key]: value };
      this.$emit('update:modelValue', newData);
    },
    // --- Các hàm hỗ trợ cho Number Formatting ---
    formatNumber(val) {
      if (!val) return '';
      // Loại bỏ mọi ký tự không phải số để bắt đầu sạch
      const cleanVal = val.toString().replace(/\D/g, '');
      if (!cleanVal) return '';
      // Format dùng chuẩn vi-VN (dấu chấm phân tách nghìn)
      return new Intl.NumberFormat('vi-VN').format(parseInt(cleanVal));
    },
    handleNumberInput(key, rawValue) {
      // Khi người dùng gõ, chỉ lấy các chữ số
      const digitsOnly = rawValue.replace(/\D/g, '');
      // Phát sự kiện cập nhật giá trị thô (chỉ số) lên cha
      this.updateValue(key, digitsOnly);
    },
    // --- Các hàm khác ---
    openPicker(key) {
      const picker = this.$refs['picker_' + key];
      if (picker && picker[0]) {
        picker[0].showPicker();
      }
    },
    handlePickerChange(key, isoDate) {
      if (!isoDate) return;
      // isoDate is YYYY-MM-DD, convert to DD/MM/YYYY
      const [y, m, d] = isoDate.split('-');
      const formatted = `${d}/${m}/${y}`;
      this.updateValue(key, formatted);
    },
    hasDynamicTemplate(field) {
      return field.default_value && field.default_value.includes('{{');
    },
    applyTemplate(field) {
      const template = field.default_value;
      const rendered = this.renderTemplate(template, this.modelValue);
      this.updateValue(field.placeholder_key, rendered);
    },
    renderTemplate(template, context) {
      return template.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (match, key) => {
        // Hỗ trợ cả key thuần (so_tien) và prefix (as.so_tien, p.ho_ten)
        // Chúng ta sẽ bỏ qua prefix nếu có (về cơ bản lấy phần sau dấu chấm cuối cùng hoặc nguyên chuỗi)
        const pureKey = key.includes('.') ? key.split('.').pop() : key;
        return context[pureKey] !== undefined ? context[pureKey] : match;
      });
    }
  }
}
</script>

<style scoped>
/* Sử dụng Grid 12 cột */
.dynamic-inputs {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 15px;
}

.form-field {
  /* Mặc định sẽ ghi đè bởi inline-style gridColumn */
  text-align: left;
}

.form-field label {
  display: block;
  font-weight: bold;
  margin-bottom: 4px;
  font-size: 0.9rem;
}

.input-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.custom-textarea {
  min-height: 100px;
  resize: vertical;
  line-height: 1.5;
}

.input-with-tools {
  display: flex;
  position: relative;
  align-items: center;
}

.btn-magic {
  position: absolute;
  right: 5px;
  background: transparent;
  border: none;
  color: #42b983;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.btn-magic:hover {
  transform: scale(1.2);
  color: #369870;
}

.btn-magic svg {
  filter: drop-shadow(0 0 2px rgba(66, 185, 131, 0.3));
}

/* Hybrid Date Input Styles */
.date-input-wrapper {
  display: flex;
  position: relative;
  align-items: center;
}

.hybrid-text {
  flex: 1;
  padding-right: 40px;
  /* Space for icon */
}

.calendar-trigger {
  position: absolute;
  right: 1px;
  top: 1px;
  bottom: 1px;
  width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #f8f9fa;
  border-left: 1px solid #ccc;
  border-radius: 0 4px 4px 0;
  color: #555;
  transition: all 0.2s;
}

.calendar-trigger:hover {
  background: #e9ecef;
  color: #000;
}

.hidden-picker {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}
</style>
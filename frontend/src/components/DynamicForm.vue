<template>
  <div class="dynamic-inputs">
    <div v-for="field in sortedFields" :key="field.id" class="form-field"
      :style="{ gridColumn: `span ${field.width_cols || 12}` }" :class="field.css_class">
      <!-- Unique label for each instance -->
      <label :for="idPrefix + field.placeholder_key">{{ field.label }}</label>

      <!-- Text Input -->
      <div v-if="field.data_type === 'TEXT'" class="input-with-tools">
        <input type="text" :id="idPrefix + field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)"
          @blur="handleBlur(field.placeholder_key, $event.target.value)" class="input-control" :class="inputClass"
          :disabled="disabled" />
        <button v-if="hasDynamicTemplate(field) && !disabled" class="btn-magic" title="Tự động điền theo mẫu"
          @click="applyTemplate(field)">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 4V2m0 12v-2M8 8V6m0 12v-2M3 21l6-6m-4 4l5-5m1.5-1.5L21 3m-9 9l4.5-4.5" />
          </svg>
        </button>
      </div>

      <!-- Textarea Input (MỚI) -->
      <div v-else-if="field.data_type === 'TEXTAREA'" class="input-with-tools">
        <textarea :id="idPrefix + field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)"
          @blur="handleBlur(field.placeholder_key, $event.target.value)" class="input-control custom-textarea"
          :class="inputClass" rows="3" :disabled="disabled"></textarea>
        <button v-if="hasDynamicTemplate(field) && !disabled" class="btn-magic" title="Tự động điền theo mẫu"
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
        <input v-if="field.use_digit_grouping" type="text" :id="idPrefix + field.placeholder_key"
          :value="formatNumber(modelValue[field.placeholder_key])"
          @input="handleNumberInput(field.placeholder_key, $event.target.value)"
          @blur="handleBlur(field.placeholder_key, $event.target.value)" class="input-control" :class="inputClass"
          placeholder="0" :disabled="disabled" />
        <!-- Nếu không: Dùng number input truyền thống -->
        <input v-else type="number" :id="idPrefix + field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)"
          @blur="handleBlur(field.placeholder_key, $event.target.value)" class="input-control" :class="inputClass"
          :disabled="disabled" />

        <!-- Hiển thị số thành chữ (MỚI - Có thể bật/tắt) -->
        <div v-if="field.show_amount_in_words && modelValue[field.placeholder_key]" class="amount-in-words">
          {{ numberToWords(modelValue[field.placeholder_key]) }}
        </div>
      </template>

      <!-- Date Input (Option 2: Hybrid Text + Date Picker) -->
      <div v-else-if="field.data_type === 'DATE'" class="date-input-wrapper">
        <input type="text" :id="idPrefix + field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)" class="input-control hybrid-text"
          :class="inputClass" placeholder="Ngày/Tháng/Năm" :disabled="disabled" />
        <div class="calendar-trigger" :class="{ 'disabled': disabled }"
          @click="!disabled && openPicker(field.placeholder_key)">
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
        <input type="checkbox" :id="idPrefix + field.placeholder_key"
          :checked="modelValue[field.placeholder_key] === 'true' || modelValue[field.placeholder_key] === true"
          @change="updateValue(field.placeholder_key, $event.target.checked)" :disabled="disabled" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DynamicForm',
  props: {
    idPrefix: { type: String, default: 'fld-' }, // Prefix để đảm bảo ID không trùng lặp khi có nhiều form
    fields: { type: Array, required: true },
    modelValue: { type: Object, required: true },
    inputClass: { type: String, default: '' },
    disabled: { type: Boolean, default: false }
  },
  emits: ['update:modelValue', 'field-blur'],
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
    handleBlur(key, value) {
      this.$emit('field-blur', { key, value });
    },
    formatNumber(val) {
      if (val === undefined || val === null || val === '') return '';
      const sVal = val.toString();
      const parts = sVal.split('.');

      // Lấy phần nguyên, xóa mọi ký tự không phải số (phòng hờ)
      const integerPart = parts[0].replace(/\D/g, '') || "0";

      // Định dạng phần nguyên dùng dấu chấm phân tách nghìn (Chuẩn VN)
      // Dùng en-US rồi replace để đảm bảo kết quả ổn định trên mọi trình duyệt
      let formattedInt = new Intl.NumberFormat('en-US').format(parseInt(integerPart));
      formattedInt = formattedInt.replace(/,/g, '.');

      if (parts.length > 1) {
        // Phần thập phân phân tách bằng dấu phẩy (Chuẩn VN)
        return formattedInt + ',' + parts[1].replace(/\D/g, '');
      }
      return formattedInt;
    },
    handleNumberInput(key, rawValue) {
      // 1. Xóa tất cả dấu chấm (dấu phân tách hàng nghìn của UI)
      let clean = rawValue.replace(/\./g, '');
      // 2. Chuyển dấu phẩy thành dấu chấm (để lưu trữ thô chuẩn JS)
      clean = clean.replace(',', '.');
      // 3. Chỉ giữ lại số và dấu chấm thập phân duy nhất
      clean = clean.replace(/[^0-9.]/g, '');
      const parts = clean.split('.');
      if (parts.length > 2) {
        clean = parts[0] + '.' + parts.slice(1).join('');
      }
      this.updateValue(key, clean);
    },
    // --- Chuyển số thành chữ (JS Implementation) ---
    numberToWords(val) {
      if (!val) return "";
      let sVal = val.toString().replace(',', '.'); // Chuẩn hóa dấu phẩy thành chấm
      if (!/[0-9]/.test(sVal)) return "";

      const units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"];
      const placeValues = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"];

      const readThreeDigits = (n, showZeroHundred) => {
        let res = "";
        const hundred = Math.floor(n / 100);
        const ten = Math.floor((n % 100) / 10);
        const unit = n % 10;
        if (hundred > 0) {
          res += units[hundred] + " trăm ";
        } else if (showZeroHundred) {
          res += "không trăm ";
        }
        if (ten > 1) {
          res += units[ten] + " mươi ";
        } else if (ten === 1) {
          res += "mười ";
        } else if ((hundred > 0 || showZeroHundred) && unit > 0 && ten === 0) {
          res += "lẻ ";
        }
        if (unit === 1 && ten > 1) {
          res += "mốt";
        } else if (unit === 5 && ten > 0) {
          res += "lăm";
        } else if (unit > 0) {
          res += units[unit];
        }
        return res.trim();
      };

      const readInteger = (sNum) => {
        if (sNum === "0" || sNum === "") return "không";
        let chunks = [];
        let temp = sNum;
        while (temp.length > 0) {
          chunks.push(parseInt(temp.slice(-3)));
          temp = temp.slice(0, -3);
        }
        let res = "";
        for (let i = chunks.length - 1; i >= 0; i--) {
          if (chunks[i] > 0) {
            res += readThreeDigits(chunks[i], i < chunks.length - 1) + " " + placeValues[i] + " ";
          }
        }
        return res.trim();
      };

      // Tách phần nguyên và phần thập phân
      const parts = sVal.split('.');
      const integerPart = parts[0].replace(/\D/g, '') || "0";
      const decimalPart = parts.length > 1 ? parts[1].replace(/\D/g, '') : "";

      let result = readInteger(integerPart);

      if (decimalPart) {
        result += " phẩy";
        for (let i = 0; i < decimalPart.length; i++) {
          const digit = parseInt(decimalPart[i]);
          result += " " + (digit === 0 ? "không" : units[digit]);
        }
      }

      const finalResult = result.trim();
      return finalResult.charAt(0).toUpperCase() + finalResult.slice(1);
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
  min-height: 80px;
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

.calendar-trigger.disabled {
  background: #f1f1f1;
  color: #aaa;
  cursor: not-allowed;
  border-left: 1px solid #ddd;
}

.hidden-picker {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.amount-in-words {
  font-size: 0.85em;
  color: #de5d06;
  font-style: italic;
  margin-top: 4px;
  background: #fdfdfd;
  padding: 2px 5px;
  border-left: 2px solid #42b983;
}
</style>
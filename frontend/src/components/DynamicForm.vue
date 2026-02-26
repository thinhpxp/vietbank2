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
        <!-- Computed Field: Tự động tính toán, readonly -->
        <div v-if="isComputedField(field)" class="computed-field-wrapper">
          <input type="text" :id="idPrefix + field.placeholder_key"
            :value="formatNumber(computedValues[field.placeholder_key])" class="input-control input-computed"
            :class="inputClass" readonly title="Trường tự động tính toán" />
          <span class="badge-computed">⚡ Tự động</span>
        </div>
        <!-- Nếu bật phân tách hàng nghìn: Dùng text input để format linh hoạt -->
        <input v-else-if="field.use_digit_grouping" type="text" :id="idPrefix + field.placeholder_key"
          :value="formatNumber(modelValue[field.placeholder_key])"
          @input="handleNumberInput(field.placeholder_key, $event.target.value)"
          @blur="handleBlur(field.placeholder_key, $event.target.value)" class="input-control" :class="inputClass"
          placeholder="0" :disabled="disabled" />
        <!-- Nếu không: Dùng number input truyền thống -->
        <input v-else type="number" :id="idPrefix + field.placeholder_key" :value="modelValue[field.placeholder_key]"
          @input="updateValue(field.placeholder_key, $event.target.value)"
          @blur="handleBlur(field.placeholder_key, $event.target.value)" class="input-control" :class="inputClass"
          :disabled="disabled" />

        <!-- Hiển thị số thành chữ -->
        <div v-if="field.show_amount_in_words && getDisplayValue(field)" class="amount-in-words">
          {{ numberToWords(getDisplayValue(field)) }}
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
    idPrefix: { type: String, default: 'fld-' },
    fields: { type: Array, required: true },
    modelValue: { type: Object, required: true },
    inputClass: { type: String, default: '' },
    disabled: { type: Boolean, default: false },
    allSections: { type: Object, default: () => ({}) } // objectSections từ LoanProfileForm
  },
  emits: ['update:modelValue', 'field-blur', 'computed-update'],
  computed: {
    sortedFields() {
      return [...this.fields].sort((a, b) => (a.order || 0) - (b.order || 0));
    },
    // Tính toán giá trị các computed fields (reactive — tự cập nhật khi allSections thay đổi)
    computedValues() {
      const result = {};
      this.fields.forEach(field => {
        if (this.isComputedField(field)) {
          result[field.placeholder_key] = this.evaluateFormula(field.default_value, this.allSections);
        }
      });
      return result;
    }
  },
  watch: {
    // Khi computed values thay đổi, emit lên parent để cập nhật generalFieldValues
    computedValues: {
      handler(newVals) {
        if (Object.keys(newVals).length > 0) {
          this.$emit('computed-update', newVals);
        }
      },
      deep: true
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
      return field.default_value && field.default_value.includes('{{') && !this.isComputedField(field);
    },
    isComputedField(field) {
      return field.default_value && field.default_value.trim().startsWith('=');
    },
    // Lấy giá trị hiển thị: computed hoặc thường
    getDisplayValue(field) {
      if (this.isComputedField(field)) {
        return this.computedValues[field.placeholder_key];
      }
      return this.modelValue[field.placeholder_key];
    },
    /**
     * Formula Engine — Parse và tính toán công thức
     * Cú pháp: =FUNC(TYPE.field, TYPE2.field, ...)
     * Hỗ trợ: SUM, COUNT, AVG, MIN, MAX, CONCAT
     */
    evaluateFormula(formula, sections) {
      if (!formula || !formula.trim().startsWith('=')) return null;
      const expr = formula.trim().substring(1);
      return this.evaluateSubExpr(expr, sections);
    },
    evaluateSubExpr(expr, sections) {
      if (!expr) return null;
      const match = expr.trim().match(/^(\w+)\((.*)\)$/s);
      if (!match) return null;
      const func = match[1].toUpperCase();
      const argsRaw = match[2];
      const args = this.parseFormulaArgs(argsRaw);

      // Thu thập giá trị số từ các tham số (hỗ trợ Global Lookup & Aggregate Keywords)
      // Thu thập giá trị thô (Số hoặc Chuỗi) từ context
      const collectRaw = (argStr) => {
        if (!argStr) return [];
        const trimmed = argStr.trim();
        if (trimmed.startsWith('"') || trimmed.startsWith("'")) {
          return [trimmed.replace(/['"]/g, '')];
        }

        // Hỗ trợ gọi hàm đệ quy
        if (trimmed.includes('(') && trimmed.includes(')')) {
          const res = this.evaluateSubExpr(trimmed, sections);
          return res !== null ? [res] : [];
        }

        let results = [];
        let typeCode = null;
        let fieldKey = trimmed;
        if (trimmed.includes('.')) {
          const parts = trimmed.split('.');
          typeCode = parts[0].toUpperCase();
          fieldKey = parts[1];
        }

        const extractFromObj = (obj, fk) => {
          const fv = obj.individual_field_values || obj.field_values || obj;
          const actualKey = Object.keys(fv).find(k => k.toLowerCase() === fk.toLowerCase());
          return actualKey ? fv[actualKey] : null;
        };

        // Logic thu thập (Đồng bộ với Backend: Chống nhân bản)
        if (typeCode === 'ASSET' || !typeCode) {
          Object.keys(sections).forEach(sKey => {
            // Chỉ quét các mảng đối tượng thực thụ, bỏ qua các danh sách _list thừa
            if (sKey !== '_GENERAL_' && sKey !== 'PERSON' && Array.isArray(sections[sKey]) && !sKey.endsWith('_list')) {
              sections[sKey].forEach(obj => {
                const v = extractFromObj(obj, fieldKey);
                if (v !== null && v !== undefined) results.push(v);
              });
            }
          });
        }
        if (typeCode === 'PERSON' || (!typeCode && results.length === 0)) {
          const people = sections['PERSON'] || sections['people'] || [];
          if (Array.isArray(people)) {
            people.forEach(obj => {
              const v = extractFromObj(obj, fieldKey);
              if (v !== null && v !== undefined) results.push(v);
            });
          }
        }
        if (typeCode === '_GENERAL_' || (!typeCode && results.length === 0)) {
          const gen = sections['_GENERAL_'];
          if (gen) {
            const v = extractFromObj(gen, fieldKey);
            if (v !== null && v !== undefined) results.push(v);
          }
        }
        // Specific Type fallback
        if (typeCode && !['ASSET', 'PERSON', '_GENERAL_'].includes(typeCode)) {
          const sKey = Object.keys(sections).find(k => k.toUpperCase() === typeCode);
          if (sKey && Array.isArray(sections[sKey])) {
            sections[sKey].forEach(obj => {
              const v = extractFromObj(obj, fieldKey);
              if (v !== null && v !== undefined) results.push(v);
            });
          }
        }
        return results;
      };

      const toFloat = (val) => {
        if (val === null || val === undefined || val === '') return 0;
        if (typeof val === 'number') return val;
        if (Array.isArray(val)) return toFloat(val[0]);

        // Chuẩn hóa: loại bỏ khoảng trắng và không gian không ngắt
        let s = String(val).replace(/\s/g, '').replace(/\u00a0/g, '').trim();
        if (!s) return 0;

        // Heuristic xử lý dấu phân cách nghìn/thập phân (Ưu tiên VN 1.000,50)
        if (s.includes(',') && s.includes('.')) {
          if (s.lastIndexOf(',') > s.lastIndexOf('.')) { // format VN
            s = s.replace(/\./g, '').replace(/,/g, '.');
          } else { // format US
            s = s.replace(/,/g, '');
          }
        } else if (s.includes(',')) {
          // Chỉ có dấu phẩy: 1,000,000 hoặc 1,5?
          const count = (s.match(/,/g) || []).length;
          const parts = s.split(',');
          if (count > 1) s = s.replace(/,/g, '');
          else if (parts[1].length === 3) s = s.replace(/,/g, ''); // 1,000 -> 1000
          else s = s.replace(/,/g, '.'); // 1,5 -> 1.5
        } else if (s.includes('.')) {
          // Chỉ có dấu chấm: 1.000.000 hoặc 1.5?
          const count = (s.match(/\./g) || []).length;
          const parts = s.split('.');
          if (count > 1) s = s.replace(/\./g, '');
          else if (parts[1].length === 3) s = s.replace(/\./g, ''); // 1.000 -> 1000
          // Ngược lại giữ nguyên (1.5 -> 1.5)
        }

        const n = parseFloat(s);
        return isNaN(n) ? 0 : n;
      };

      const collectNumbers = (argList) => {
        const nums = [];
        argList.forEach(a => {
          const raws = collectRaw(a);
          if (raws.length === 0) {
            // Thử parse trực tiếp nếu không phải field lookup (hỗ trợ hằng số 0,5)
            nums.push(toFloat(a));
          } else {
            raws.forEach(r => nums.push(toFloat(r)));
          }
        });
        return nums;
      };

      const collectTexts = (argList, separator) => {
        const texts = [];
        argList.forEach(a => {
          const raws = collectRaw(a);
          raws.forEach(r => { if (r !== null && r !== undefined) texts.push(String(r)); });
        });
        return texts.join(separator);
      };

      switch (func) {
        case 'SUM': {
          const vals = collectNumbers(args);
          return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) : 0;
        }
        case 'PRODUCT':
        case 'MUL': {
          const vals = collectNumbers(args);
          return vals.length > 0 ? vals.reduce((a, b) => a * b, 1) : 0;
        }
        case 'SUBTRACT':
        case 'SUB': {
          const vals = collectNumbers(args);
          if (vals.length === 0) return 0;
          let res = vals[0];
          for (let i = 1; i < vals.length; i++) res -= vals[i];
          return res;
        }
        case 'DIVIDE':
        case 'DIV': {
          const vals = collectNumbers(args);
          if (vals.length === 0) return 0;
          let res = vals[0];
          for (let i = 1; i < vals.length; i++) {
            if (vals[i] !== 0) res /= vals[i];
          }
          return res;
        }
        case 'ROUND': {
          const vals = collectNumbers(args.slice(0, 1));
          if (vals.length === 0) return 0;
          const pRaw = args.length > 1 ? this.evaluateSubExpr(args[1], sections) || args[1] : 0;
          const precision = parseInt(String(pRaw).replace(/['"]/g, ''));
          const factor = Math.pow(10, isNaN(precision) ? 0 : precision);
          return Math.round(vals[0] * factor) / factor;
        }
        case 'COUNT': {
          let total = 0;
          args.forEach(arg => {
            const trimmed = arg.trim();
            if (trimmed.startsWith('"') || trimmed.startsWith("'")) return;
            const typeCode = trimmed.includes('.') ? trimmed.split('.')[0].toUpperCase() : trimmed.toUpperCase();
            if (typeCode === 'ASSET') {
              Object.keys(sections).forEach(k => {
                if (k !== '_GENERAL_' && k !== 'PERSON' && Array.isArray(sections[k]) && !k.endsWith('_list')) {
                  total += sections[k].length;
                }
              });
            } else if (typeCode === 'PERSON') {
              const p = sections['PERSON'] || sections['people'] || [];
              if (Array.isArray(p)) total += p.length;
            } else {
              const sKey = Object.keys(sections).find(k => k.toUpperCase() === typeCode);
              if (sKey && Array.isArray(sections[sKey])) total += sections[sKey].length;
            }
          });
          return total;
        }
        case 'AVG': {
          const vals = collectNumbers(args);
          return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
        }
        case 'MIN': {
          const vals = collectNumbers(args);
          return vals.length > 0 ? Math.min(...vals) : 0;
        }
        case 'MAX': {
          const vals = collectNumbers(args);
          return vals.length > 0 ? Math.max(...vals) : 0;
        }
        case 'CONCAT': {
          const sepArg = args.find(a => a.trim().startsWith('"') || a.trim().startsWith("'"));
          const separator = sepArg ? sepArg.trim().replace(/["']/g, '') : ', ';
          const fieldArgs = args.filter(a => a !== sepArg);
          return collectTexts(fieldArgs, separator);
        }
        case 'IF': {
          if (args.length < 3) return '';
          const condRaw = args[0].trim();
          let isTrue = false;
          let ops = ['>=', '<=', '>', '<', '='];
          let usedOp = ops.find(op => condRaw.includes(op));
          if (usedOp) {
            const [lS, rS] = condRaw.split(usedOp);
            const lV = collectNumbers([lS.trim()])[0];
            const rV = collectNumbers([rS.trim()])[0];

            if (usedOp === '>=') isTrue = lV >= rV;
            else if (usedOp === '<=') isTrue = lV <= rV;
            else if (usedOp === '>') isTrue = lV > rV;
            else if (usedOp === '<') isTrue = lV < rV;
            else if (usedOp === '=') isTrue = Math.abs(lV - rV) < 0.000001 || String(lV) === String(rV);
          } else {
            const rawCond = collectRaw(condRaw);
            isTrue = !!(rawCond[0] || condRaw.replace(/['"]/g, ''));
          }
          const resKey = isTrue ? args[1] : args[2];
          const lookup = collectRaw(resKey);
          return lookup.length > 0 ? lookup[0] : resKey.trim().replace(/['"]/g, '');
        }
        default:
          return '';
      }
    },
    // Tách tham số, tôn trọng string trong quotes
    parseFormulaArgs(raw) {
      if (!raw) return [];
      const args = [];
      let current = '';
      let inQuote = false;
      let quoteChar = '';
      let depth = 0;
      for (let i = 0; i < raw.length; i++) {
        const ch = raw[i];
        if ((ch === '"' || ch === "'") && !inQuote) {
          inQuote = true; quoteChar = ch; current += ch;
        } else if (ch === quoteChar && inQuote) {
          inQuote = false; current += ch;
        } else if (!inQuote) {
          if (ch === '(') depth++;
          else if (ch === ')') depth--;
          if (ch === ',' && depth === 0) {
            args.push(current.trim()); current = '';
            continue;
          }
          current += ch;
        } else {
          current += ch;
        }
      }
      if (current.trim()) args.push(current.trim());
      return args;
    },
    applyTemplate(field) {
      const template = field.default_value;
      const rendered = this.renderTemplate(template, this.modelValue);
      this.updateValue(field.placeholder_key, rendered);
    },
    renderTemplate(template, context) {
      return template.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (match, key) => {
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

/* Computed Fields */
.computed-field-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-computed {
  background: #f0fdf4 !important;
  border-style: dashed !important;
  border-color: #86efac !important;
  color: #166534 !important;
  font-weight: 600;
  cursor: default;
}

.badge-computed {
  position: absolute;
  right: 8px;
  font-size: 0.7rem;
  color: #16a34a;
  font-weight: 600;
  pointer-events: none;
  white-space: nowrap;
}
</style>
<template>
  <div class="dynamic-inputs">
    <FormField v-for="field in sortedFields" :key="field.id" :field="field" :idPrefix="idPrefix"
      :modelValue="modelValue[field.placeholder_key]" @update:modelValue="updateValue(field.placeholder_key, $event)"
      @blur="handleBlur(field.placeholder_key, $event)" @apply-template="applyTemplate" :inputClass="inputClass"
      :disabled="disabled" :isComputed="isComputedField(field)" />
  </div>
</template>

<script>
import FormField from './FormField.vue';
import { evaluateFormula } from '@/utils/formulaEngine';

export default {
  name: 'DynamicForm',
  components: { FormField },
  props: {
    idPrefix: { type: String, default: 'fld-' },
    fields: { type: Array, required: true },
    modelValue: { type: Object, required: true },
    inputClass: { type: String, default: '' },
    disabled: { type: Boolean, default: false },
    allSections: { type: Object, default: () => ({}) }
  },
  emits: ['update:modelValue', 'field-blur', 'computed-update'],
  computed: {
    sortedFields() {
      return [...this.fields].sort((a, b) => (a.order || 0) - (b.order || 0));
    },
    computedValues() {
      const result = {};
      this.fields.forEach(field => {
        if (this.isComputedField(field)) {
          result[field.placeholder_key] = evaluateFormula(field.default_value, this.allSections);
        }
      });
      return result;
    }
  },
  watch: {
    computedValues: {
      handler(newVals, oldVals) {
        if (!newVals) return;
        const newKeys = Object.keys(newVals);
        if (newKeys.length === 0) return;

        let hasChanged = !oldVals;
        if (oldVals) {
          for (const key of newKeys) {
            if (newVals[key] !== oldVals[key]) {
              hasChanged = true;
              break;
            }
          }
        }

        if (hasChanged) {
          this.$emit('computed-update', newVals);
        }
      },
      deep: true,
      immediate: false
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
    isComputedField(field) {
      if (!field.default_value || typeof field.default_value !== 'string') return false;
      return field.default_value.trim().startsWith('=');
    },
    applyTemplate(field) {
      const template = field.default_value;
      let rendered = template.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (match, key) => {
        const pureKey = key.includes('.') ? key.split('.').pop() : key;

        let val = this.modelValue[pureKey];
        if (val !== undefined && val !== null && val !== '') return val;

        if (this.allSections) {
          for (const sKey in this.allSections) {
            const sectionData = this.allSections[sKey];
            if (Array.isArray(sectionData)) {
              for (const obj of sectionData) {
                const fv = obj.individual_field_values || obj.field_values || obj;
                if (fv && fv[pureKey] !== undefined && fv[pureKey] !== null && fv[pureKey] !== '') return fv[pureKey];
              }
            } else if (sectionData && typeof sectionData === 'object') {
              const fv = sectionData.individual_field_values || sectionData.field_values || sectionData;
              if (fv && fv[pureKey] !== undefined && fv[pureKey] !== null && fv[pureKey] !== '') return fv[pureKey];
            }
          }
        }
        return '...'; // Thay thế bằng '...' hoặc chuỗi rỗng khi trống dữ liệu
      });
      // Clean up multiple spaces
      rendered = rendered.replace(/\s+/g, ' ').replace(/\s+,/g, ',').replace(/\s+\./g, '.').trim();
      this.updateValue(field.placeholder_key, rendered);
    }
  }
}
</script>

<style scoped>
.dynamic-inputs {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 15px;
}
</style>
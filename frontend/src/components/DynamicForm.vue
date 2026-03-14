<template>
  <div class="dynamic-form-container">
    <!-- Trường hợp render theo nhóm (Groups) -->
    <template v-if="hasGroups">
      <div v-for="(groupFields, groupName) in groups" :key="groupName" class="form-group-section mb-6">
        <h4 v-if="showGroupTitle" class="group-title text-sm font-bold text-gray-500 mb-3 border-b pb-1 uppercase">
          {{ groupName }}
        </h4>
        <div class="dynamic-inputs">
          <FormField v-for="field in sortFields(groupFields)" :key="field.id" :field="field" :idPrefix="idPrefix"
            :modelValue="currentValues[field.placeholder_key]" @update:modelValue="updateValue(field.placeholder_key, $event)"
            @blur="handleBlur(field.placeholder_key, $event)" @apply-template="applyTemplate" :inputClass="inputClass"
            :disabled="disabled" :isComputed="isComputedField(field)" />
        </div>
      </div>
    </template>

    <!-- Trường hợp render phẳng (Fields) -->
    <template v-else>
      <div class="dynamic-inputs">
        <FormField v-for="field in sortedFields" :key="field.id" :field="field" :idPrefix="idPrefix"
          :modelValue="currentValues[field.placeholder_key]" @update:modelValue="updateValue(field.placeholder_key, $event)"
          @blur="handleBlur(field.placeholder_key, $event)" @apply-template="applyTemplate" :inputClass="inputClass"
          :disabled="disabled" :isComputed="isComputedField(field)" />
      </div>
    </template>
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
    // Cấu trúc cũ: danh sách phẳng
    fields: { type: Array, default: () => [] },
    // Cấu trúc mới: theo nhóm { "Nhóm A": [fields], "Nhóm B": [fields] }
    groups: { type: Object, default: null },
    // Giá trị ban đầu (alias cho modelValue)
    initialValues: { type: Object, default: null },
    modelValue: { type: Object, default: () => ({}) },
    inputClass: { type: String, default: '' },
    disabled: { type: Boolean, default: false },
    showGroupTitle: { type: Boolean, default: true },
    allSections: { type: Object, default: () => ({}) }
  },
  emits: ['update:modelValue', 'update:values', 'field-blur', 'computed-update'],
  computed: {
    hasGroups() {
      return this.groups && Object.keys(this.groups).length > 0;
    },
    // Gộp tất cả field từ các nhóm thành mảng phẳng để xử lý computed
    allFields() {
      if (this.hasGroups) {
        let flat = [];
        Object.values(this.groups).forEach(groupFields => {
          if (Array.isArray(groupFields)) {
            flat = flat.concat(groupFields);
          }
        });
        return flat;
      }
      return this.fields || [];
    },
    sortedFields() {
      return this.sortFields(this.allFields);
    },
    currentValues() {
      return this.initialValues || this.modelValue || {};
    },
    computedValues() {
      const result = {};
      const fieldsToProcess = this.allFields;
      if (!Array.isArray(fieldsToProcess)) return result;

      fieldsToProcess.forEach(field => {
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
    sortFields(fields) {
      if (!Array.isArray(fields)) return [];
      return [...fields].sort((a, b) => (a.order || 0) - (b.order || 0));
    },
    updateValue(key, value) {
      const newData = { ...this.currentValues, [key]: value };
      this.$emit('update:modelValue', newData);
      this.$emit('update:values', newData);
    },
    handleBlur(key, value) {
      this.$emit('field-blur', { key, value });
    },
    isComputedField(field) {
      if (!field || !field.default_value || typeof field.default_value !== 'string') return false;
      return field.default_value.trim().startsWith('=');
    },
    applyTemplate(field) {
      const template = field.default_value;
      let rendered = template.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (match, key) => {
        const pureKey = key.includes('.') ? key.split('.').pop() : key;

        let val = this.currentValues[pureKey];
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
        return '...';
      });
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
<template>
  <div class="dynamic-inputs">
    <div 
      v-for="field in sortedFields" 
      :key="field.id" 
      class="form-field"
      :style="{ gridColumn: `span ${field.width_cols || 12}` }"
      :class="field.css_class"
    >
      <label :for="field.placeholder_key">{{ field.label }}</label>

      <!-- Text Input -->
      <input
        v-if="field.data_type === 'TEXT'"
        type="text"
        :id="field.placeholder_key"
        :value="modelValue[field.placeholder_key]"
        @input="updateValue(field.placeholder_key, $event.target.value)"
        class="input-control"
      />

      <!-- Number Input -->
      <input
        v-else-if="field.data_type === 'NUMBER'"
        type="number"
        :id="field.placeholder_key"
        :value="modelValue[field.placeholder_key]"
        @input="updateValue(field.placeholder_key, $event.target.value)"
        class="input-control"
      />

      <!-- Date Input -->
      <input
        v-else-if="field.data_type === 'DATE'"
        type="date"
        :id="field.placeholder_key"
        :value="modelValue[field.placeholder_key]"
        @input="updateValue(field.placeholder_key, $event.target.value)"
        class="input-control"
      />

      <!-- Checkbox -->
      <div v-else-if="field.data_type === 'CHECKBOX'">
        <input
          type="checkbox"
          :id="field.placeholder_key"
          :checked="modelValue[field.placeholder_key] === 'true' || modelValue[field.placeholder_key] === true"
          @change="updateValue(field.placeholder_key, $event.target.checked)"
        />
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
.form-field label { display: block; font-weight: bold; margin-bottom: 4px; font-size: 0.9rem; }
.input-control { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
</style>
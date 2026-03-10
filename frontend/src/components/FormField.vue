<template>
    <div class="form-field" :style="{ gridColumn: `span ${field.width_cols || 12}` }" :class="field.css_class">
        <label :for="idPrefix + field.placeholder_key">{{ field.label }}</label>

        <!-- Text Input -->
        <div v-if="field.data_type === 'TEXT'" class="input-with-tools">
            <input type="text" :id="idPrefix + field.placeholder_key" :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)" @blur="$emit('blur', $event.target.value)"
                class="input-control" :class="inputClass" :disabled="disabled" />
            <button v-if="hasDynamicTemplate && !disabled" class="btn-magic" title="Tự động điền theo mẫu"
                @click="$emit('apply-template', field)">
                <SvgIcon name="sparkles" size="sm" />
            </button>
        </div>

        <!-- Textarea Input -->
        <div v-else-if="field.data_type === 'TEXTAREA'" class="input-with-tools">
            <textarea :id="idPrefix + field.placeholder_key" :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)" @blur="$emit('blur', $event.target.value)"
                class="input-control custom-textarea" :class="inputClass" rows="3" :disabled="disabled"></textarea>
            <button v-if="hasDynamicTemplate && !disabled" class="btn-magic" title="Tự động điền theo mẫu"
                @click="$emit('apply-template', field)">
                <SvgIcon name="sparkles" size="sm" />
            </button>
        </div>

        <!-- Number Input -->
        <template v-else-if="field.data_type === 'NUMBER'">
            <!-- Computed Field: Readonly handle by DynamicForm computedValues -->
            <div v-if="isComputed" class="computed-field-wrapper">
                <input type="text" :id="idPrefix + field.placeholder_key" :value="formattedValue"
                    class="input-control input-computed" :class="inputClass" readonly
                    title="Trường tự động tính toán" />
                <span class="badge-computed">⚡ Tự động</span>
            </div>

            <!-- Formatted Number Input -->
            <input v-else-if="field.use_digit_grouping" type="text" :id="idPrefix + field.placeholder_key"
                :value="formattedValue" @input="handleNumberInput" @blur="$emit('blur', $event.target.value)"
                class="input-control" :class="inputClass" placeholder="0" :disabled="disabled" />

            <!-- Standard Number Input -->
            <input v-else type="number" :id="idPrefix + field.placeholder_key" :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)" @blur="$emit('blur', $event.target.value)"
                class="input-control" :class="inputClass" :disabled="disabled" />

            <!-- Amount in words -->
            <div v-if="field.show_amount_in_words && modelValue" class="amount-in-words">
                {{ wordsValue }}
            </div>
        </template>

        <!-- Date Input -->
        <div v-else-if="field.data_type === 'DATE'" class="date-input-wrapper">
            <input type="text" :id="idPrefix + field.placeholder_key" :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)" class="input-control hybrid-text"
                :class="inputClass" placeholder="Ngày/Tháng/Năm" :disabled="disabled" />
            <div class="calendar-trigger" :class="{ 'disabled': disabled }" @click="!disabled && openPicker()">
                <SvgIcon name="calendar" size="sm" />
                <input type="date" class="hidden-picker" ref="datePicker" @change="handlePickerChange" />
            </div>
        </div>

        <!-- Checkbox -->
        <div v-else-if="field.data_type === 'CHECKBOX'" class="checkbox-wrapper">
            <input type="checkbox" :id="idPrefix + field.placeholder_key" :checked="isTrue"
                @change="handleCheckboxChange" :disabled="disabled" />
        </div>
    </div>
</template>

<script>
import SvgIcon from './common/SvgIcon.vue';
import { formatNumberVN, parseNumberVN, numberToWords } from '@/utils/formatters';

export default {
    name: 'FormField',
    components: { SvgIcon },
    props: {
        field: { type: Object, required: true },
        modelValue: { type: [String, Number, Boolean], default: '' },
        idPrefix: { type: String, default: 'f' },
        inputClass: { type: String, default: '' },
        disabled: { type: Boolean, default: false },
        isComputed: { type: Boolean, default: false }
    },
    emits: ['update:modelValue', 'blur', 'apply-template'],
    computed: {
        formattedValue() {
            if (this.field.data_type === 'NUMBER') {
                return formatNumberVN(this.modelValue);
            }
            return this.modelValue;
        },
        wordsValue() {
            if (this.field.data_type === 'NUMBER' && this.field.show_amount_in_words) {
                return numberToWords(this.modelValue);
            }
            return '';
        },
        hasDynamicTemplate() {
            if (!this.field.default_value || typeof this.field.default_value !== 'string') return false;
            return this.field.default_value.includes('{{') && !this.isComputed;
        },
        isTrue() {
            return this.modelValue === 'true' || this.modelValue === true;
        }
    },
    methods: {
        handleNumberInput(e) {
            const clean = parseNumberVN(e.target.value);
            this.$emit('update:modelValue', clean);
        },
        handleCheckboxChange(e) {
            this.$emit('update:modelValue', e.target.checked);
        },
        openPicker() {
            if (this.$refs.datePicker) {
                this.$refs.datePicker.showPicker();
            }
        },
        handlePickerChange(e) {
            const isoDate = e.target.value;
            if (!isoDate) return;
            const [y, m, d] = isoDate.split('-');
            this.$emit('update:modelValue', `${d}/${m}/${y}`);
        }
    }
}
</script>

<style scoped>
.form-field {
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
    right: 4px;
    top: 4px;
    background: #42b983;
    border: none;
    color: white;
    cursor: pointer;
    padding: 4px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-magic:hover {
    background: #369870;
    transform: scale(1.05) translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.date-input-wrapper {
    display: flex;
    position: relative;
    align-items: center;
}

.hybrid-text {
    flex: 1;
    padding-right: 40px;
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

.computed-field-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
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

.checkbox-wrapper {
    padding: 8px 0;
}
</style>

<template>
    <div class="form-group">
        <label v-if="showLabel">🏢 {{ label }}</label>
        <vxe-select v-model="selectedBranch" class="admin-select-full" filterable clearable :placeholder="placeholder"
            @change="onBranchChange">
            <vxe-option :value="null" :label="nullLabel"></vxe-option>
            <vxe-option v-for="b in activeBranches" :key="b.id" :value="b.id" :label="formatBranchLabel(b)">
            </vxe-option>
        </vxe-select>
        <small v-if="activeBranches.length === 0 && !loading" class="text-muted">
            Chưa có chi nhánh nào được cấu hình. Liên hệ Admin để thiết lập.
        </small>
    </div>
</template>

<script>
import MasterService from '@/services/master.service';

export default {
    name: 'BranchSelect',
    props: {
        modelValue: { type: [Number, null], default: null },
        label: { type: String, default: 'Đơn vị công tác' },
        showLabel: { type: Boolean, default: true },
        placeholder: { type: String, default: '-- Chọn đơn vị --' },
        nullLabel: { type: String, default: '-- Chưa chọn --' }
    },
    emits: ['update:modelValue'],
    data() {
        return {
            branches: [],
            loading: false
        };
    },
    computed: {
        selectedBranch: {
            get() { return this.modelValue; },
            set(val) { this.$emit('update:modelValue', val); }
        },
        activeBranches() {
            return this.branches.filter(b => !b.is_deleted);
        }
    },
    async mounted() {
        await this.fetchBranches();
    },
    methods: {
        async fetchBranches() {
            this.loading = true;
            try {
                const res = await MasterService.getBranches();
                this.branches = res.data || [];
            } catch (e) {
                console.warn('Không thể tải danh sách:', e);
            } finally {
                this.loading = false;
            }
        },
        formatBranchLabel(branch) {
            if (branch.additional_info) {
                return `${branch.display_name} | ${branch.additional_info}`;
            }
            return branch.display_name;
        },
        onBranchChange({ value }) {
            this.$emit('update:modelValue', value);
        }
    }
};
</script>

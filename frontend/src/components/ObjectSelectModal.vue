<template>
    <BaseModal :isOpen="isOpen" :title="title" :initialWidth="900" :isResizable="true" @close="close">
        <div class="modal-body-content">
            <div class="search-box mb-4">
                <div class="input-group">
                    <input v-model="searchQuery" :placeholder="searchPlaceholder" class="form-control"
                        @keyup.enter="fetchItems">
                    <button class="btn-action btn-primary" @click="fetchItems">
                        <SvgIcon name="search" size="sm" />
                        <span>Tìm kiếm</span>
                    </button>
                </div>
            </div>

            <div v-if="loading" class="loading-state">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <span class="ms-2">Đang tải dữ liệu...</span>
            </div>

            <div v-else class="data-table-vxe">
                <vxe-table border round :data="items" :row-config="{ isHover: true }"
                    :column-config="{ resizable: true }" :sort-config="{ trigger: 'cell' }" height="auto"
                    class="select-table">

                    <vxe-column field="display_name" title="Tên / Số hiệu" min-width="200" sortable>
                        <template #default="{ row }">
                            <strong class="font-bold">
                                {{ row.ho_ten || row.so_giay_chung_nhan || row.display_name || '---' }}
                            </strong>
                        </template>
                    </vxe-column>

                    <vxe-column field="additional_info" title="Thông tin thêm" min-width="250">
                        <template #default="{ row }">
                            {{ getAdditionalInfo(row) }}
                        </template>
                    </vxe-column>

                    <vxe-column field="object_type_display" title="Loại" width="120" sortable>
                        <template #default="{ row }">
                            <span class="status-badge draft">{{ row.object_type_display }}</span>
                        </template>
                    </vxe-column>

                    <vxe-column field="created_at" title="Ngày tạo" width="150" sortable>
                        <template #default="{ row }">
                            <span class="text-muted">{{ formatDate(row.created_at) }}</span>
                        </template>
                    </vxe-column>

                    <vxe-column field="updated_at" title="Cập nhật gần nhất" width="180" sortable>
                        <template #default="{ row }">
                            <div class="update-info">
                                <span>{{ formatDate(row.updated_at) }}</span>
                                <small class="text-muted" v-if="row.last_updated_by_name">
                                    by {{ row.last_updated_by_name }}
                                </small>
                            </div>
                        </template>
                    </vxe-column>

                    <vxe-column title="Thao tác" width="100" fixed="right" align="center">
                        <template #default="{ row }">
                            <button class="btn-action btn-success btn-sm" @click="selectItem(row)">Chọn</button>
                        </template>
                    </vxe-column>

                    <template #empty>
                        <div class="text-center py-8 text-muted italic">
                            Không tìm thấy kết quả phù hợp.
                        </div>
                    </template>
                </vxe-table>
            </div>
        </div>

        <template #footer>
            <button class="btn-action btn-secondary" @click="close">Hủy</button>
        </template>
    </BaseModal>
</template>

<script>
import axios from 'axios';
import { API_URL } from '@/store/auth';
import BaseModal from '@/components/BaseModal.vue';
import SvgIcon from '@/components/common/SvgIcon.vue';

export default {
    name: 'ObjectSelectModal',
    components: {
        BaseModal,
        SvgIcon
    },
    props: {
        isOpen: Boolean,
        type: {
            type: String,
            default: 'person' // 'person', 'attorney' or 'asset'
        }
    },
    emits: ['close', 'select'],
    data() {
        return {
            items: [],
            objectTypes: [],
            searchQuery: '',
            loading: false
        };
    },
    computed: {
        title() {
            if (this.type === 'person') return 'Chọn Người từ danh sách';
            if (this.type === 'attorney') return 'Chọn Đại diện Ngân hàng';
            return 'Chọn Tài sản từ danh sách';
        },
        searchPlaceholder() {
            if (this.type === 'person') return 'Tìm theo Tên hoặc CCCD...';
            if (this.type === 'attorney') return 'Tìm theo Tên hoặc Mã nhân viên...';
            return 'Tìm theo Số Giấy chứng nhận...';
        }
    },
    watch: {
        isOpen(val) {
            if (val) {
                this.searchQuery = '';
                this.fetchItems();
            }
        }
    },
    methods: {
        close() {
            this.$emit('close');
        },
        async fetchObjectTypes() {
            if (this.objectTypes.length > 0) return;
            try {
                const response = await axios.get(`${API_URL}/object-types/`);
                this.objectTypes = response.data;
            } catch (error) {
                console.error('Lỗi khi tải loại đối tượng:', error);
            }
        },
        async fetchItems() {
            this.loading = true;
            try {
                await this.fetchObjectTypes();

                let types = '';
                if (this.type && !['person', 'attorney', 'asset'].includes(this.type)) {
                    types = this.type;
                } else if (this.type === 'person') {
                    types = 'PERSON';
                } else if (this.type === 'attorney') {
                    types = 'ATTORNEY';
                } else {
                    types = this.objectTypes
                        .filter(t => t.form_display_mode === 'ASSET_LIST' && t.code !== 'PERSON')
                        .map(t => t.code)
                        .join(',');
                    if (!types) types = 'ASSET,VEHICLE,REALESTATE,SAVINGS,CONTRACT';
                }

                const url = `${API_URL}/master-objects/?object_type=${types}&search=${encodeURIComponent(this.searchQuery)}`;
                const response = await axios.get(url);

                this.items = response.data.map(item => ({
                    ...item,
                    ...item.field_values
                }));

            } catch (error) {
                console.error('Lỗi khi tải dữ liệu master:', error);
            } finally {
                this.loading = false;
            }
        },
        getIdentityValue(item) {
            const typeConfig = this.objectTypes.find(t => t.code === item.object_type);
            if (typeConfig && typeConfig.identity_field_key) {
                return item[typeConfig.identity_field_key] || '---';
            }
            return '---';
        },
        getAdditionalInfo(item) {
            const typeConfig = this.objectTypes.find(t => t.code === item.object_type);
            if (typeConfig && typeConfig.dynamic_summary_template) {
                let result = typeConfig.dynamic_summary_template;
                const placeholders = result.match(/{([^}]+)}/g);
                if (placeholders) {
                    placeholders.forEach(ph => {
                        const key = ph.slice(1, -1);
                        const val = item[key] !== undefined ? item[key] : '...';
                        result = result.replace(ph, val);
                    });
                }
                return result;
            }

            const fallbacks = {
                'PERSON': item.cccd ? `CCCD: ${item.cccd}` : '---',
                'VEHICLE': item.nhan_hieu_xe ? `Hãng: ${item.nhan_hieu_xe}` : '---',
                'REALESTATE': item.so_vao_so ? `Số vào sổ: ${item.so_vao_so}` : '---',
                'BOND': item.ky_han_trai_phieu ? `Kỳ hạn: ${item.ky_han_trai_phieu}` : '---',
                'SAVINGS': item.so_tien_goi ? `Số tiền: ${item.so_tien_goi}` : '---',
                'ATTORNEY': item.nguoi_dai_dien ? `Họ tên: ${item.nguoi_dai_dien}` : '---'
            };

            return fallbacks[item.object_type] || item.owner_name || '---';
        },
        selectItem(item) {
            this.$emit('select', item);
            this.close();
        },
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleString('vi-VN');
        }
    }
};
</script>

<style scoped>
.modal-body-content {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.search-box .input-group {
    display: flex;
    gap: var(--spacing-sm);
}

.form-control {
    flex: 1;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    outline: none;
}

.form-control:focus {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.data-table-vxe {
    flex: 1;
    min-height: 250px;
}

.update-info {
    display: flex;
    flex-direction: column;
    font-size: var(--font-xs);
}

.font-bold {
    font-weight: 600;
    color: var(--color-text);
}

.loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-xl);
    color: var(--color-text-muted);
}

.text-muted {
    color: var(--color-text-muted);
    font-size: var(--font-sm);
}

.ms-2 {
    margin-left: var(--spacing-sm);
}

.mb-4 {
    margin-bottom: var(--spacing-lg);
}

.py-8 {
    padding-top: var(--spacing-xl);
    padding-bottom: var(--spacing-xl);
}

.text-center {
    text-align: center;
}

.italic {
    font-style: italic;
}
</style>

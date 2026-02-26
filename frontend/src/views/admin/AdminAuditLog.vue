<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>📜 Nhật ký hệ thống (System Audit Log)</h2>
      <div class="header-actions">
        <button class="btn-primary" @click="fetchLogs">🔄 Làm mới</button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>Hành động:</label>
        <select v-model="filterAction" @change="fetchLogs" class="admin-form-control filter-control">
          <option value="">Tất cả</option>
          <option value="LOGIN">Đăng nhập</option>
          <option value="LOGOUT">Đăng xuất</option>
          <option value="CREATE">Tạo mới</option>
          <option value="UPDATE">Cập nhật</option>
          <option value="DELETE">Xóa</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Tên đăng nhập:</label>
        <input type="text" v-model="filterUserName" class="admin-form-control filter-control"
          placeholder="Nhập tên đăng nhập..." @keyup.enter="fetchLogs">
      </div>
      <div class="filter-group">
        <label>Từ ngày:</label>
        <input type="date" v-model="fromDate" class="admin-form-control filter-control" @change="fetchLogs">
      </div>
      <div class="filter-group">
        <label>Đến ngày:</label>
        <input type="date" v-model="toDate" class="admin-form-control filter-control" @change="fetchLogs">
      </div>
    </div>

    <!-- Data Table -->
    <div class="data-table-vxe">
      <div v-if="loading" class="loading-state">Đang tải dữ liệu...</div>

      <vxe-table v-else border round :data="filteredLogs" :row-config="{ isHover: true }"
        :column-config="{ resizable: true }" :sort-config="{ trigger: 'cell' }" height="auto" class="audit-table">

        <vxe-column field="id" title="ID" width="70" sortable>
          <template #default="{ row }">
            #{{ row.id }}
          </template>
        </vxe-column>

        <vxe-column field="timestamp" title="Thời gian" width="160" sortable>
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}<br>
            <small class="text-muted">{{ formatDate(row.timestamp) }}</small>
          </template>
        </vxe-column>

        <vxe-column field="user" title="Người thực hiện" width="180" sortable>
          <template #default="{ row }">
            <div class="user-cell">
              <span class="user-avatar-sm">👤</span>
              <div>
                <strong>{{ row.user_details?.username || 'System' }}</strong>
                <br><small>ID: {{ row.user }}</small>
              </div>
            </div>
          </template>
        </vxe-column>

        <vxe-column field="action" title="Hành động" width="130" sortable>
          <template #default="{ row }">
            <span class="badge" :class="getActionClass(row.action)">{{ row.action }}</span>
          </template>
        </vxe-column>

        <vxe-column field="target_model" title="Đối tượng" width="220" sortable>
          <template #default="{ row }">
            <strong>{{ row.target_model }}</strong>
            <span v-if="row.target_id" class="target-id">#{{ row.target_id }}</span>
          </template>
        </vxe-column>

        <vxe-column field="details" title="Chi tiết" min-width="300">
          <template #default="{ row }">
            <div class="cell-details">{{ row.details }}</div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <!-- Pagination (Simple Previous/Next based on DRF) -->
    <div class="pagination-controls" v-if="nextPage || prevPage">
      <button :disabled="!prevPage" @click="loadPage(prevPage)" class="btn-secondary btn-sm">Previous</button>
      <span class="page-info">Trang hiện tại</span>
      <button :disabled="!nextPage" @click="loadPage(nextPage)" class="btn-secondary btn-sm">Next</button>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { format, parseISO, subDays } from 'date-fns';
import { errorHandlingMixin } from '@/utils/errorHandler';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';

export default {
  name: 'AdminAuditLog',
  mixins: [errorHandlingMixin, FilterableTableMixin],
  data() {
    return {
      logs: [],
      loading: false,
      filterAction: '',
      filterUserName: '',
      fromDate: format(subDays(new Date(), 15), 'yyyy-MM-dd'),
      toDate: format(new Date(), 'yyyy-MM-dd'),
      nextPage: null,
      prevPage: null
    };
  },
  computed: {
    filteredLogs() {
      return this.logs;
    }
  },
  created() {
    this.fetchLogs();
  },
  methods: {
    async fetchLogs() {
      this.loading = true;
      try {
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';
        let url = `${API_URL}/audit-logs/`;

        // Build query params
        const params = {};
        if (this.filterUserName) params.username = this.filterUserName;

        if (this.filterAction) params.action = this.filterAction;
        if (this.fromDate) params.timestamp_gte = this.fromDate + "T00:00:00";
        if (this.toDate) params.timestamp_lte = this.toDate + "T23:59:59";

        const response = await axios.get(url, { params });

        // DRF Pagination support
        if (response.data.results) {
          this.logs = response.data.results;
          this.nextPage = response.data.next;
          this.prevPage = response.data.previous;
        } else {
          this.logs = response.data;
        }

        // Removed client-side filtering as backend now handles it efficiently via indexing.

      } catch (error) {
        this.showError(error);
      } finally {
        this.loading = false;
      }
    },
    async loadPage(url) {
      if (!url) return;
      this.loading = true;
      try {
        const response = await axios.get(url);
        if (response.data.results) {
          this.logs = response.data.results;
          this.nextPage = response.data.next;
          this.prevPage = response.data.previous;
        }
      } catch (error) {
        this.showError(error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(isoString) {
      if (!isoString) return '';
      return format(parseISO(isoString), 'dd/MM/yyyy');
    },
    formatTime(isoString) {
      if (!isoString) return '';
      return format(parseISO(isoString), 'HH:mm:ss');
    },
    getActionClass(action) {
      const map = {
        'CREATE': 'badge-active', // Green
        'UPDATE': 'badge-custom', // Blue
        'DELETE': 'badge-inactive', // Red
        'LOGIN': 'badge-all', // Teal
        'LOGOUT': 'badge-user' // Gray
      };
      return map[action] || 'badge-user';
    },
  }
};
</script>

<style scoped>
.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar-sm {
  background: #eee;
  padding: 5px;
  border-radius: 50%;
}

.cell-details {
  max-width: 400px;
  white-space: pre-wrap;
  font-size: 0.9rem;
  color: #555;
}

.text-muted {
  color: #999;
}

.target-id {
  background: #f0f0f0;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 0.8em;
  margin-left: 5px;
}

.pagination-controls {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
  align-items: center;
}
</style>

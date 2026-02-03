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
    <div class="ui-table-wrapper">
      <div v-if="loading" class="loading-state">Đang tải dữ liệu...</div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th width="50" class="admin-sortable" @click="toggleSort('id')">
              ID {{ getSortIcon('id') }}
            </th>
            <th width="150" class="admin-sortable" @click="toggleSort('timestamp')">
              Thời gian {{ getSortIcon('timestamp') }}
            </th>
            <th width="150" class="admin-sortable" @click="toggleSort('user')">
              Người thực hiện {{ getSortIcon('user') }}
            </th>
            <th width="120" class="admin-sortable" @click="toggleSort('action')">
              Hành động {{ getSortIcon('action') }}
            </th>
            <th width="200" class="admin-sortable" @click="toggleSort('target_model')">
              Đối tượng {{ getSortIcon('target_model') }}
            </th>
            <th>Chi tiết</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="logs.length === 0">
            <td colspan="6" class="text-center">Không có dữ liệu nhật ký.</td>
          </tr>
          <tr v-for="log in sortedLogs" :key="log.id">
            <td>#{{ log.id }}</td>
            <td>{{ formatTime(log.timestamp) }}<br><small class="text-muted">{{ formatDate(log.timestamp) }}</small>
            </td>
            <td>
              <div class="user-cell">
                <span class="user-avatar-sm">👤</span>
                <div>
                  <strong>{{ log.user_details?.username || 'System' }}</strong>
                  <br><small>ID: {{ log.user }}</small>
                </div>
              </div>
            </td>
            <td>
              <span class="badge" :class="getActionClass(log.action)">{{ log.action }}</span>
            </td>
            <td>
              <strong>{{ log.target_model }}</strong>
              <span v-if="log.target_id" class="target-id">#{{ log.target_id }}</span>
            </td>
            <td class="cell-details">
              {{ log.details }}
            </td>
          </tr>
        </tbody>
      </table>
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
import { makeTableResizable } from '@/utils/resizable-table';
import { FilterableTableMixin } from '@/mixins/FilterableTableMixin';
import { SortableTableMixin } from '@/mixins/SortableTableMixin';

export default {
  name: 'AdminAuditLog',
  mixins: [errorHandlingMixin, FilterableTableMixin, SortableTableMixin],
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
    sortedLogs() {
      // Map 'user' sort key to 'user_details.username' if needed, 
      // but SortableTableMixin supports simple key mapping or direct access.
      // For user, let's sort by username if possible, or fallback to user ID.
      // Since our mixin is simple, let's pre-process or just sort by basic fields.
      // We will add a simple mapping if the mixin supports it or just use 'user' (ID).
      // actually, let's use the mixin's mapping feature if available.
      // Looking at mixin: sortArray(items, mapping).

      const mapping = {
        'user': 'user', // Defaults to ID. To sort by username we'd need to flatten or custom sort.
        // Let's stick to default for now as planned.
      };

      // Apply filtering first? No, filter is applied in fetchLogs (server/client hybrid).
      // Actually, fetchLogs updates 'this.logs'. 
      // If we use filterArray in fetchLogs, 'this.logs' will contain filtered items.
      // Then we sort 'this.logs'.
      return this.sortArray(this.logs, mapping);
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
        this.$nextTick(() => this.initResizable());
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
        this.$nextTick(() => this.initResizable());
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
    initResizable() {
      const table = this.$el.querySelector('.data-table');
      if (table) {
        makeTableResizable(table, 'admin-audit-logs');
      }
    }
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

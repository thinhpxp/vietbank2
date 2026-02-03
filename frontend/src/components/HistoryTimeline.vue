<template>
  <div class="history-timeline">
    <div v-if="loading" class="timeline-loading">
      Đang tải nhật ký...
    </div>

    <div v-else-if="logs.length === 0" class="timeline-empty">
      Chưa có nhật ký ghi nhận.
    </div>

    <div v-else class="timeline-content">
      <div v-for="(group, date) in groupedLogs" :key="date" class="timeline-group">
        <div class="timeline-date">{{ formatDate(date) }}</div>
        
        <div v-for="log in group" :key="log.id" class="timeline-item">
          <div class="timeline-marker" :class="getActionColor(log.action)"></div>
          <div class="timeline-body">
            <div class="timeline-header">
              <span class="user-name">{{ log.user_details?.username || 'System' }}</span>
              <span class="action-badge" :class="getActionColor(log.action)">
                {{ getActionLabel(log.action) }}
              </span>
              <span class="time">{{ formatTime(log.timestamp) }}</span>
            </div>
            <div class="timeline-message">
              {{ log.details }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { format, parseISO, isToday, isYesterday } from 'date-fns';
import { vi } from 'date-fns/locale';

export default {
  name: 'HistoryTimeline',
  props: {
    apiUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      logs: [],
      loading: false
    };
  },
  computed: {
    groupedLogs() {
      const groups = {};
      this.logs.forEach(log => {
        const date = log.timestamp.split('T')[0];
        if (!groups[date]) groups[date] = [];
        groups[date].push(log);
      });
      return groups;
    }
  },
  watch: {
    apiUrl: {
      immediate: true,
      handler(newUrl) {
        if (newUrl) this.fetchLogs();
      }
    }
  },
  methods: {
    async fetchLogs() {
      this.loading = true;
      try {
        const response = await axios.get(this.apiUrl);
        this.logs = response.data;
      } catch (error) {
        console.error("Error fetching history:", error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateStr) {
      const date = parseISO(dateStr);
      if (isToday(date)) return 'Hôm nay';
      if (isYesterday(date)) return 'Hôm qua';
      return format(date, 'dd/MM/yyyy', { locale: vi });
    },
    formatTime(isoString) {
      return format(parseISO(isoString), 'HH:mm');
    },
    getActionLabel(action) {
      const map = {
        'CREATE': 'Tạo mới',
        'UPDATE': 'Cập nhật',
        'DELETE': 'Xóa',
        'LOGIN': 'Đăng nhập',
        'LOGOUT': 'Đăng xuất'
      };
      return map[action] || action;
    },
    getActionColor(action) {
      const map = {
        'CREATE': 'success',
        'UPDATE': 'info',
        'DELETE': 'danger',
        'LOGIN': 'warning',
        'LOGOUT': 'secondary'
      };
      return map[action] || 'primary';
    }
  }
};
</script>

<style scoped>
.history-timeline {
  padding: 10px;
  font-family: 'Inter', sans-serif;
}

.timeline-loading, .timeline-empty {
  text-align: center;
  color: #6c757d;
  padding: 20px;
  font-style: italic;
}

.timeline-group {
  margin-bottom: 20px;
}

.timeline-date {
  font-weight: bold;
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  margin-bottom: 15px;
  position: relative;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

/* Vertical Line */
.timeline-item::before {
  content: '';
  position: absolute;
  left: 5px; /* Center of marker (10px / 2) */
  top: 15px;
  bottom: -20px; 
  width: 2px;
  background: #f0f0f0;
  z-index: 0;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
  z-index: 1;
  border: 2px solid white;
  box-shadow: 0 0 0 1px #eee;
}

.timeline-marker.success { background-color: #28a745; }
.timeline-marker.info { background-color: #17a2b8; }
.timeline-marker.danger { background-color: #dc3545; }
.timeline-marker.warning { background-color: #ffc107; }
.timeline-marker.secondary { background-color: #6c757d; }

.timeline-body {
  flex: 1;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.time {
  margin-left: auto;
  font-size: 0.8rem;
  color: #999;
}

.action-badge {
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
}

.action-badge.success { background-color: #28a745; }
.action-badge.info { background-color: #17a2b8; }
.action-badge.danger { background-color: #dc3545; }
.action-badge.warning { background-color: #ffc107; color: #333; }
.action-badge.secondary { background-color: #6c757d; }

.timeline-message {
  color: #555;
  line-height: 1.4;
}
</style>

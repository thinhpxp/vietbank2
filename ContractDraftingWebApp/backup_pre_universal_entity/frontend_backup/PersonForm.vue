<template>
  <div class="person-card">
    <div class="card-header" @click="isCollapsed = !isCollapsed">
      <div class="header-left">
        <span class="toggle-icon" :class="{ 'collapsed': isCollapsed }">▼</span>
        <h4>Người liên quan #{{ index + 1 }} <span v-if="displayName" class="person-name">- {{ displayName }}</span>
        </h4>
        <button type="button" class="btn-search-master" @click.stop="isModalOpen = true"
          title="Chọn từ danh sách đã có">🔍</button>
      </div>
      <button type="button" class="btn-remove" @click.stop="$emit('remove')">Xóa</button>
    </div>

    <div class="card-body" v-show="!isCollapsed">
      <!-- 2. Chọn Vai trò (Roles) -->
      <div class="roles-section">
        <label>Vai trò trong hồ sơ:</label>
        <div class="checkbox-group">
          <label v-for="role in availableRoles" :key="role" class="checkbox-inline">
            <input type="checkbox" :value="role" v-model="localPerson.roles"> {{ role }}
          </label>
        </div>
      </div>

      <!-- 3. Các trường động của Người (Địa chỉ, SĐT...) -->
      <div class="dynamic-section" v-if="personFields.length > 0">
        <hr>
        <DynamicForm :fields="personFields" v-model="localPerson.individual_field_values" />
      </div>
    </div>

    <ObjectSelectModal :isOpen="isModalOpen" type="person" @close="isModalOpen = false" @select="onPersonSelect" />
  </div>
</template>

<script>
import DynamicForm from './DynamicForm.vue';
import ObjectSelectModal from './ObjectSelectModal.vue';

export default {
  name: 'PersonForm',
  components: { DynamicForm, ObjectSelectModal },
  props: {
    index: Number,
    person: Object,
    personFields: Array,
    availableRoles: { type: Array, default: () => [] }
  },
  emits: ['update:person', 'remove'],
  data() {
    return {
      localPerson: JSON.parse(JSON.stringify(this.person)),
      isCollapsed: false,
      isModalOpen: false
    }
  },
  computed: {
    // Hiển thị tên hoặc CCCD khi collapse
    displayName() {
      const fv = this.localPerson.individual_field_values || {};
      return fv.ho_ten || fv.cccd_so || '';
    }
  },
  watch: {
    localPerson: {
      handler(newVal) {
        this.$emit('update:person', newVal);
      },
      deep: true
    }
  },
  methods: {
    onPersonSelect(person) {
      if (!this.localPerson.individual_field_values) {
        this.localPerson.individual_field_values = {};
      }

      // Auto-fill thông tin từ master
      // Chúng ta sẽ giả định các key cơ bản ho_ten, cccd_so có dữ liệu
      if (person.ho_ten) this.localPerson.individual_field_values.ho_ten = person.ho_ten;
      if (person.cccd_so) this.localPerson.individual_field_values.cccd_so = person.cccd_so;

      // Nếu Backend trả về nhiều Field hơn, chúng ta cũng có thể mapping thêm ở đây
      alert(`Đã chọn: ${person.ho_ten}`);
    }
  }
}
</script>

<style scoped>
.person-card {
  border: 1px solid #ddd;
  background: #fff;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  background: #efcebc;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ddd;
  cursor: pointer;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header h4 {
  margin: 0;
  color: #333;
}

.person-name {
  font-weight: normal;
  color: #555;
  font-size: 0.9em;
}

.card-body {
  padding: 15px;
}

.btn-remove {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.col {
  flex: 1;
  text-align: left;
}

.col label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.input-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.roles-section {
  text-align: left;
  margin-bottom: 15px;
}

.checkbox-inline {
  margin-right: 15px;
  cursor: pointer;
}

.btn-search-master {
  background: #3498db;
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-left: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-search-master:hover {
  background: #2980b9;
}

/* Toggle Icon */
.toggle-icon {
  font-size: 12px;
  transition: transform 0.2s;
  color: #666;
}

.toggle-icon.collapsed {
  transform: rotate(-90deg);
}
</style>
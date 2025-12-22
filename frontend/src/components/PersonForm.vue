<template>
  <div class="person-card">
    <div class="card-header" @click="isCollapsed = !isCollapsed">
      <div class="header-left">
        <span class="toggle-icon" :class="{ 'collapsed': isCollapsed }">▼</span>
        <h4>Người liên quan #{{ index + 1 }} <span v-if="displayName" class="person-name">- {{ displayName }}</span></h4>
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
        <DynamicForm
          :fields="personFields"
          v-model="localPerson.individual_field_values"
        />
      </div>
    </div>
  </div>
</template>

<script>
import DynamicForm from './DynamicForm.vue';

export default {
  name: 'PersonForm',
  components: { DynamicForm },
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
      isCollapsed: false // Mặc định mở
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
  }
}
</script>

<style scoped>
.person-card { border: 1px solid #ddd; background: #fff; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }
.card-header { background: #efcebc; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; cursor: pointer; user-select: none; }
.header-left { display: flex; align-items: center; gap: 10px; }
.card-header h4 { margin: 0; color: #333; }
.person-name { font-weight: normal; color: #555; font-size: 0.9em; }
.card-body { padding: 15px; }
.btn-remove { background: #ff4d4f; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
.form-row { display: flex; gap: 15px; margin-bottom: 15px; }
.col { flex: 1; text-align: left; }
.col label { display: block; font-weight: bold; margin-bottom: 5px; }
.input-control { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;}
.roles-section { text-align: left; margin-bottom: 15px; }
.checkbox-inline { margin-right: 15px; cursor: pointer; }

/* Toggle Icon */
.toggle-icon { font-size: 12px; transition: transform 0.2s; color: #666; }
.toggle-icon.collapsed { transform: rotate(-90deg); }
</style>
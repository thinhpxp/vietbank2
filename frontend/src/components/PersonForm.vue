<template>
  <div class="person-card">
    <div class="card-header">
      <h4>Người liên quan #{{ index + 1 }}</h4>
      <button type="button" class="btn-remove" @click="$emit('remove')">Xóa</button>
    </div>

    <div class="card-body">
      <!-- 1. Thông tin Cố định -->
      <!-- 1. Thông tin Cố định - ĐÃ BỎ do chuyển sang động -->
      <!-- <div class="form-row">...</div> -->


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
      <!-- Tái sử dụng DynamicForm ở đây -->
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
    person: Object, // Dữ liệu của người này được truyền từ cha xuống
    personFields: Array, // Danh sách các trường động thuộc nhóm KHACH_HANG
    availableRoles: {
        type: Array,
        default: () => []
    }
  },
  emits: ['update:person', 'remove'],
  data() {
    return {
      // availableRoles đã được chuyển thành props
      // Tạo bản sao cục bộ để tránh mutate props trực tiếp
      localPerson: JSON.parse(JSON.stringify(this.person))
    }
  },
  watch: {
    // Khi dữ liệu cục bộ thay đổi, báo cho cha biết
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
.card-header { background: #f0f0f0; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; }
.card-header h4 { margin: 0; color: #333; }
.card-body { padding: 15px; }
.btn-remove { background: #ff4d4f; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
.form-row { display: flex; gap: 15px; margin-bottom: 15px; }
.col { flex: 1; text-align: left; }
.col label { display: block; font-weight: bold; margin-bottom: 5px; }
.input-control { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;}
.roles-section { text-align: left; margin-bottom: 15px; }
.checkbox-inline { margin-right: 15px; cursor: pointer; }
</style>
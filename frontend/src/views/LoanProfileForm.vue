<template>
  <div class="page-container">
    <header class="page-header">
      <h2>Tạo / Cập nhật Hồ sơ Vay</h2>
      <button class="btn-primary" @click="saveProfile" :disabled="isSaving">
        {{ isSaving ? 'Đang lưu...' : 'Lưu Hồ Sơ' }}
      </button>
    </header>

    <div v-if="loading">Đang tải cấu hình...</div>

    <div v-else class="form-layout">
      <!-- CỘT TRÁI: THÔNG TIN CHUNG -->
      <div class="left-panel">
        <div class="panel-section">
          <h3>Thông tin cơ bản</h3>
          <div class="field-group">
            <label>Tên hồ sơ <span style="color:red">*</span></label>
            <input 
              type="text" 
              v-model="profileName" 
              class="input-control" 
              placeholder="Nhập tên hồ sơ (VD: Hồ sơ ông A vay mua xe)..." 
            />
          </div>
        </div>

        <div v-for="(fields, groupName) in groupedFields" :key="groupName" class="panel-section">
          <h3>{{ groupName }}</h3>
          <DynamicForm
            :fields="fields"
            v-model="generalFieldValues"
          />
        </div>
      </div>

      <!-- CỘT PHẢI: DANH SÁCH NGƯỜI -->
      <div class="right-panel">
        <div class="panel-header">
          <h3>Danh sách Người liên quan</h3>
          <button class="btn-secondary" @click="addPerson">+ Thêm Người</button>
        </div>

        <div v-if="people.length === 0" class="empty-state">
          Chưa có người nào. Hãy thêm Bên vay hoặc Bên bảo đảm.
        </div>

        <div v-for="(person, index) in people" :key="index">
          <PersonForm
            :index="index"
            :person="person"
            :personFields="personFields"
            @update:person="updatePerson(index, $event)"
            @remove="removePerson(index)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import DynamicForm from '../components/DynamicForm.vue';
import PersonForm from '../components/PersonForm.vue';

export default {
  name: 'LoanProfileForm',
  components: { DynamicForm, PersonForm },
  props: ['id'],
  data() {
    return {
      loading: true,
      isSaving: false,
      allFields: [],
      profileName: '',
      generalFieldValues: {},
      people: [],
      currentId: null
    };
  },
  computed: {
    groupedFields() {
      // Nhóm các fields theo group_name
      return this.allFields.reduce((groups, field) => {
        const gName = field.group_name || 'Khác';
        // [FIX] Loại bỏ các trường thuộc nhóm Person khỏi cột bên trái
        // Chuẩn hóa tên nhóm để so sánh (lowercase)
        const lowerGName = gName.toLowerCase();
        if (lowerGName === 'thông tin cá nhân' || lowerGName === 'khach_hang') {
            return groups;
        }

        if (!groups[gName]) {
          groups[gName] = [];
        }
        groups[gName].push(field);
        return groups;
      }, {});
    },
    personFields() {
      // [FIX] Lọc các trường thuộc nhóm Person để truyền vào PersonForm
      // Sử dụng toLowerCase để đảm bảo bắt đúng tên nhóm
      return this.allFields.filter(f => {
          const gName = (f.group_name || '').toLowerCase();
          return gName === 'thông tin cá nhân' || gName === 'khach_hang';
      });
    }
  },
  mounted() {
    this.fetchFields();
    if (this.id) {
      this.currentId = this.id;
      this.fetchProfileData(this.id);
    } else {
      this.addPerson();
    }
  },
  methods: {
    async fetchFields() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/fields/');
        this.allFields = response.data;
      } catch (e) {
        console.error(e);
        alert('Lỗi tải cấu hình fields');
      } finally {
        this.loading = false;
      }
    },
    addPerson() {
      this.people.push({
        id: null,
        ho_ten: '',
        cccd_so: '',
        roles: [],
        individual_field_values: {}
      });
    },
    removePerson(index) {
      if (confirm('Bạn có chắc muốn xóa người này?')) {
        this.people.splice(index, 1);
      }
    },
    updatePerson(index, updatedPerson) {
      this.people[index] = updatedPerson;
    },
    async fetchProfileData(id) {
      try {
        this.loading = true;
        const response = await axios.get(`http://127.0.0.1:8000/api/loan-profiles/${id}/`);
        const data = response.data;
        this.profileName = data.name;
        this.generalFieldValues = data.field_values || {};
        this.people = data.people && data.people.length > 0 ? data.people : [];
        if (this.people.length === 0) this.addPerson();
      } catch (e) {
        console.error('Lỗi load hồ sơ:', e);
        alert('Không tải được dữ liệu hồ sơ!');
      } finally {
        this.loading = false;
      }
    },
    async saveProfile() {
      if (!this.profileName) return alert('Vui lòng nhập tên hồ sơ!');
      this.isSaving = true;
      try {
        let targetId = this.currentId;
        if (!targetId) {
          const createRes = await axios.post('http://127.0.0.1:8000/api/loan-profiles/', { name: this.profileName });
          targetId = createRes.data.id;
        }
        const payload = {
          name: this.profileName,
          field_values: this.generalFieldValues,
          people: this.people
        };
        await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${targetId}/save_form_data/`, payload);
        alert('Lưu thành công!');
        this.$router.push('/');
      } catch (error) {
        console.error(error);
        alert('Lỗi khi lưu: ' + (error.response?.data?.message || error.message));
      } finally {
        this.isSaving = false;
      }
    }
  }
};
</script>

<style scoped>
.page-container { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.form-layout { display: flex; gap: 30px; }
.left-panel { flex: 1; }
.right-panel { flex: 2; } /* Cột người rộng hơn */
.panel-section { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #eee; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.panel-section h3, .panel-header h3 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #42b983; padding-bottom: 5px; display: inline-block; }

.input-control { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.btn-primary { background: #42b983; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: #2c3e50; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
.empty-state { padding: 40px; text-align: center; background: #eee; color: #777; border-radius: 8px; border: 2px dashed #ccc; }
.field-group { margin-bottom: 15px; text-align: left; }
.field-group label { display: block; font-weight: bold; margin-bottom: 5px; }
</style>
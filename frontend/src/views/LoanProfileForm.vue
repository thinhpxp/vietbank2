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
          <h3>Thông tin Hồ sơ</h3>
          <div class="field-group">
             <label>Tên Hồ sơ (*)</label>
             <input type="text" v-model="profileName" class="input-control" placeholder="VD: HS vay ông A">
          </div>
        </div>

        <div class="panel-section" v-if="generalFields.length > 0">
          <h3>Chi tiết Khoản vay & TSBĐ</h3>
          <!-- Tái sử dụng DynamicForm cho các trường chung -->
          <DynamicForm
            :fields="generalFields"
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
  data() {
    return {
      loading: true,
      isSaving: false,

      // Dữ liệu cấu hình từ API
      allFields: [],

      // Dữ liệu hồ sơ
      profileName: '',
      generalFieldValues: {}, // Chứa giá trị của KHOAN_VAY, TSBD...
      people: [] // Mảng chứa các đối tượng Person
    }
  },
  computed: {
    // Lọc ra các trường chung (KHOAN_VAY, TSBD, KHAC...)
    generalFields() {
      return this.allFields.filter(f => f.group_name !== 'KHACH_HANG');
    },
    // Lọc ra các trường thuộc về Người (KHACH_HANG)
    personFields() {
      return this.allFields.filter(f => f.group_name === 'KHACH_HANG');
    }
  },
  mounted() {
    this.fetchFields();
    // Khởi tạo sẵn 1 người để user đỡ phải bấm thêm
    this.addPerson();
  },
  methods: {
    async fetchFields() {
      try {
        // Lưu ý: API này trả về mảng phẳng các trường
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
        id: null, // null nghĩa là người mới
        ho_ten: '',
        cccd_so: '',
        roles: [],
        individual_field_values: {}
      });
    },
    removePerson(index) {
      if(confirm('Bạn có chắc muốn xóa người này?')) {
        this.people.splice(index, 1);
      }
    },
    updatePerson(index, updatedPerson) {
      // Cập nhật lại thông tin người trong mảng
      this.people[index] = updatedPerson;
    },
    async saveProfile() {
      if (!this.profileName) return alert('Vui lòng nhập tên hồ sơ!');

      this.isSaving = true;

      try {
        // BƯỚC 1: TẠO "CÁI VỎ" HỒ SƠ MỚI TRƯỚC
        // Gọi API gốc của DRF để tạo object LoanProfile
        const createResponse = await axios.post('http://127.0.0.1:8000/api/loan-profiles/', {
          name: this.profileName
        });

        const newLoanId = createResponse.data.id;
        console.log("Đã tạo hồ sơ mới với ID:", newLoanId);

        // BƯỚC 2: LƯU DỮ LIỆU CHI TIẾT VÀO ID VỪA TẠO
        // Chuẩn bị payload
        const payload = {
          name: this.profileName,
          field_values: this.generalFieldValues,
          people: this.people
        };

        const saveUrl = `http://127.0.0.1:8000/api/loan-profiles/${newLoanId}/save_form_data/`;
        const saveResponse = await axios.post(saveUrl, payload);
        console.log("Server phản hồi:", saveResponse.data); // <-- Thêm dòng này
        alert('Tạo hồ sơ thành công! ID: ' + newLoanId);

        // (Tùy chọn) Reset form hoặc chuyển hướng sau khi lưu thành công
        // this.$router.push({ name: 'Dashboard' });

      } catch (error) {
        console.error(error);
        alert('Lỗi khi lưu: ' + (error.response?.data?.message || error.message));
      } finally {
        this.isSaving = false;
      }
    }
  }
}
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
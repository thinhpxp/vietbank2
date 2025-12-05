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
  // Thêm dòng này để nhận ID từ Router (nếu có)
  props: ['id'],
  data() {
    return {
      loading: true,
      isSaving: false,

      // Dữ liệu cấu hình từ API
      allFields: [],

      // Dữ liệu hồ sơ
      profileName: '',
      generalFieldValues: {}, // Chứa giá trị của KHOAN_VAY, TSBD...
      people: [], // Mảng chứa các đối tượng Person
      currentId: null // Biến để lưu ID đang sửa
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

    // KIỂM TRA: Nếu có ID truyền vào (tức là đang Sửa), thì tải dữ liệu
    if (this.id) {
      this.currentId = this.id;
      this.fetchProfileData(this.id);
    } else {
      // Nếu tạo mới thì thêm sẵn 1 người trống
      this.addPerson();
    }
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
    // THÊM HÀM MỚI: Tải dữ liệu hồ sơ cũ
    async fetchProfileData(id) {
      try {
        this.loading = true;
        const response = await axios.get(`http://127.0.0.1:8000/api/loan-profiles/${id}/`);
        const data = response.data;

        // 1. Điền tên hồ sơ
        this.profileName = data.name;

        // 2. Điền Field Values chung
        // Backend trả về mảng field_values: [{field_id: 1, value: "abc", ...}]
        // Ta cần chuyển nó về dạng Object: { placeholder_key: "abc" }
        // Lưu ý: Backend cần trả về placeholder_key trong serializer hoặc ta phải map lại.
        // Để đơn giản, giả sử Serializer của bạn trả về nested object đầy đủ.

        // LOGIC TẠM THỜI (Cần chỉnh Serializer Backend để dễ dùng hơn):
        // Nếu Backend trả về dạng raw nested, việc map lại ở Frontend khá cực.
        // Tốt nhất là Serializer nên trả về format giống lúc save_form_data gửi lên.

        // Tuy nhiên, để code chạy được ngay, ta sẽ xử lý đơn giản:
        if (data.field_values) {
           data.field_values.forEach(fv => {
              if (fv.field && fv.field.placeholder_key) {
                  this.generalFieldValues[fv.field.placeholder_key] = fv.value;
              }
           });
        }

        // 3. Điền People
        // Tương tự, cần map lại cấu trúc data.loan_profile_people -> this.people
        if (data.loan_profile_people) {
           this.people = data.loan_profile_people.map(lpp => {
               const p = lpp.person;
               // Cần lấy field values riêng của người này
               // Việc này hơi phức tạp nếu Backend không trả về sẵn.
               return {
                   id: p.id,
                   ho_ten: p.name_for_display,
                   cccd_so: p.cccd_so,
                   roles: lpp.roles,
                   individual_field_values: {} // Tạm thời để trống nếu chưa map được
               };
           });
        }

      } catch (e) {
        console.error(e);
        alert("Không tải được hồ sơ!");
      } finally {
        this.loading = false;
      }
    },
    async saveProfile() {
      if (!this.profileName) return alert('Vui lòng nhập tên hồ sơ!');

      this.isSaving = true;

      try {
        let targetId = this.currentId;

            // Nếu chưa có ID (Tạo mới) -> Gọi API tạo vỏ
            if (!targetId) {
                const createRes = await axios.post('http://127.0.0.1:8000/api/loan-profiles/', { name: this.profileName });
                targetId = createRes.data.id;
            }

            // Gọi API save_form_data
            const payload = {
                name: this.profileName,
                field_values: this.generalFieldValues,
                people: this.people
            };
            await axios.post(`http://127.0.0.1:8000/api/loan-profiles/${targetId}/save_form_data/`, payload);

            alert('Lưu thành công!');
            // Quay về Dashboard
            this.$router.push('/');

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
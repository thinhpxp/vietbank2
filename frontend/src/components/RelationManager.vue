<template>
  <div class="relation-manager" v-if="currentTypeAllowsRelations">
    <div class="relation-header">
      <span class="relation-title">🔗 Các liên kết liên quan</span>
      <button v-if="!disabled" class="btn-add-rel" @click="showAddModal = true" title="Thêm liên kết">
        + Gán quan hệ
      </button>
    </div>

    <div v-if="relations.length === 0" class="no-relations">
      Chưa có liên kết dẫn chiếu nào.
    </div>

    <div v-else class="relation-list">
      <div v-for="rel in relations" :key="rel.id" class="relation-item">
        <div class="rel-info">
          <span class="rel-type-badge">{{ $t(rel.relation_type) }}</span>

          <span class="rel-target">
            {{ isSource(rel) ? 'đối với' : 'là' }}
            
            <!-- Logic hiển thị: Nếu trong hồ sơ thì text thường, ngoài hồ sơ thì link -->
            <strong v-if="isObjectInProfile(isSource(rel) ? rel.target_object : rel.source_object)">
              {{ isSource(rel) ? rel.target_name : rel.source_name }}
            </strong>
            <strong v-else class="external-link" @click="viewObjectDetail(isSource(rel) ? rel.target_object : rel.source_object)" title="Xem chi tiết đối tượng">
              {{ isSource(rel) ? rel.target_name : rel.source_name }}
            </strong>

            <small>({{ $t(isSource(rel) ? rel.target_type : rel.source_type) }})</small>

          </span>
        </div>
        <button v-if="!disabled" class="btn-remove-rel" @click="removeRelation(rel.id)"
          title="Xóa liên kết">&times;</button>
      </div>
    </div>
    
            <!-- Modal xem chi tiết -->
    <ObjectDetailModal 
      :objectId="viewingObjectId" 
      :fieldDefinitions="allFields"
      @close="viewingObjectId = null" 
    />

    <!-- Modal chọn đối tượng để liên kết -->
    <BaseModal :isOpen="showAddModal" title="Gán mối quan hệ mới" @close="closeModal">
      <p class="modal-subtitle">Chọn đối tượng trong hồ sơ này để thiết lập dẫn chiếu</p>

      <div class="admin-form-section">
        <h4>Cấu hình liên kết</h4>
        <div class="form-group">
          <label>Loại quan hệ:</label>
          <select v-model="newRelType" class="admin-form-control">
            <option value="OWNER">{{ $t('OWNER') }}</option>
            <option value="SECURES">{{ $t('SECURES') }}</option>
            <option value="AMENDS">{{ $t('AMENDS') }}</option>
            <option value="REFERENCES">{{ $t('REFERENCES') }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>Đối tượng liên kết:</label>
          <div class="object-selector-list">
            <div v-for="obj in filteredPossibleTargets" :key="obj.id" class="selectable-object"
              :class="{ selected: selectedTargetId === obj.id }" @click="selectedTargetId = obj.id">
              <div class="obj-name">{{ obj.display_name }}</div>
            </div>
          </div>
          <div v-if="filteredPossibleTargets.length === 0" class="empty-list">
            Không tìm thấy đối tượng nào khác trong hồ sơ này để liên kết.
          </div>
        </div>
      </div>

      <template #footer>
        <button class="btn-action btn-secondary" @click="closeModal">Hủy</button>
        <button class="btn-action btn-primary" @click="confirmAddRelation" :disabled="!selectedTargetId">
          Xác nhận gán
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import axios from 'axios';
import BaseModal from './BaseModal.vue';
import ObjectDetailModal from './ObjectDetailModal.vue';

export default {
  name: 'RelationManager',
  components: { BaseModal, ObjectDetailModal },
  props: {
    masterObjectId: { type: Number, required: true },
    profileObjects: { type: Array, default: () => [] },
    // Fields definitions for Object Detail Modal
    allFields: { type: Array, default: () => [] },
    currentObjectType: { type: String, default: '' },
    refreshTrigger: { type: Number, default: 0 },
    disabled: { type: Boolean, default: false }
  },
  data() {
    return {
      relations: [],
      showAddModal: false,
      newRelType: 'SECURES',
      selectedTargetId: null,
      loading: false,
      // Quick View state
      viewingObjectId: null
    };
  },
  computed: {
    filteredPossibleTargets() {
      // Chỉ hiện các object KHÁC với object hiện tại VÀ cho phép gán liên kết
      return this.profileObjects.filter(obj => {
        if (obj.id === this.masterObjectId) return false;
        if (obj.allow_relations === false) return false;
        return true;
      });
    },
    currentTypeAllowsRelations() {
      // Tìm xem object hiện tại có bị cấm gán quan hệ không
      // profileObjects chứa tất cả object, bao gồm cả object hiện tại
      const currentObj = this.profileObjects.find(obj => obj.id === this.masterObjectId);
      return currentObj ? (currentObj.allow_relations !== false) : true;
    }
  },
  watch: {
    masterObjectId: {
      immediate: true,
      handler() {
        this.fetchRelations();
      }
    },
    refreshTrigger() {
      // Refresh relations when notified by parent
      this.fetchRelations();
    }
  },
  methods: {
    async fetchRelations() {
      if (!this.masterObjectId) return;
      try {
        const res = await axios.get(`http://127.0.0.1:8000/api/master-objects/${this.masterObjectId}/`);
        // Gộp quan hệ đi và quan hệ đến
        this.relations = [
          ...(res.data.relations_out || []),
          ...(res.data.relations_in || [])
        ];
      } catch (e) {
        console.error('Lỗi tải quan hệ:', e);
      }
    },
    isSource(rel) {
      return rel.source_object === this.masterObjectId;
    },
    closeModal() {
      this.showAddModal = false;
      this.selectedTargetId = null;
    },
    async confirmAddRelation() {
      if (!this.selectedTargetId) return;
      try {
        await axios.post('http://127.0.0.1:8000/api/master-relations/create_relation/', {
          source_id: this.masterObjectId,
          target_id: this.selectedTargetId,
          relation_type: this.newRelType
        });
        this.$toast.success('Đã gán quan hệ thành công');
        this.closeModal();
        this.fetchRelations();
      } catch (e) {
        this.$toast.error('Lỗi khi gán quan hệ');
      }
    },
    async removeRelation(relId) {
      if (!confirm('Bạn có chắc muốn xóa liên kết này?')) return;
      try {
        await axios.delete(`http://127.0.0.1:8000/api/master-relations/${relId}/`);
        this.relations = this.relations.filter(r => r.id !== relId);
        this.$toast.success('Đã xóa liên kết');
      } catch (e) {
        this.$toast.error('Lỗi khi xóa liên kết');
      }
    },
    // Kiểm tra xem một ID object có nằm trong hồ sơ hiện tại không
    isObjectInProfile(objectId) {
      return this.profileObjects.some(obj => obj.id === objectId);
    },
    viewObjectDetail(objectId) {
      this.viewingObjectId = objectId;
    }
  }
};
</script>

<style scoped>
.relation-manager {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #ccc;
}

.relation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.relation-title {
  font-weight: 600;
  font-size: 0.9em;
  color: #555;
}

.btn-add-rel {
  background: #f0f4f8;
  border: 1px solid #d1d9e0;
  color: #2980b9;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  cursor: pointer;
}

.btn-add-rel:hover {
  background: #e2e8f0;
}

.no-relations {
  font-size: 0.8em;
  color: #999;
  font-style: italic;
  padding: 5px;
}

.relation-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.relation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  padding: 6px 10px;
  border-radius: 4px;
  border-left: 3px solid #3498db;
  font-size: 0.85em;
}

.rel-type-badge {
  background: #3498db;
  color: white;
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 0.75em;
  margin-right: 8px;
  font-weight: bold;
}

.rel-target {
  flex: 1;
  color: #2c3e50;
}

.rel-target strong {
  margin-left: 4px;
  color: #2980b9;
}

.rel-target small {
  color: #999;
  margin-left: 4px;
  font-style: italic;
}

.btn-remove-rel {
  background: none;
  border: none;
  color: #e74c3c;
  font-size: 1.2em;
  cursor: pointer;
  padding: 0 5px;
  line-height: 1;
}

.modal-subtitle {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
}

.object-selector-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
}

.selectable-object {
  padding: 8px 12px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.selectable-object:hover {
  background: #f0f7ff;
}

.selectable-object.selected {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.obj-name {
  font-weight: 500;
}

.empty-list {
  font-size: 0.9em;
  color: #999;
  padding: 20px;
  text-align: center;
}

/* Style cho link external */
.external-link {
  margin-left: 4px;
  color: #b7950b !important; /* Màu vàng đậm (Dark Gold) cho dễ đọc trên nền trắng */
  cursor: pointer;
  font-weight: 600;
}

.external-link:hover {
  color: #9a7d0a;
  text-decoration: underline;
}
</style>

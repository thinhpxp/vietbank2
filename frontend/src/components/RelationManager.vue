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
            {{ getRelationDescription(rel) }}

            <!-- Logic hiển thị: Nếu trong hồ sơ thì text thường, ngoài hồ sơ thì link -->
            <strong v-if="isObjectInProfile(isSource(rel) ? rel.target_object : rel.source_object)" class="internal-obj-text">
              {{ isSource(rel) ? rel.target_name : rel.source_name }}
            </strong>
            <span v-else class="external-link"
              @click.stop="viewObjectDetail(isSource(rel) ? rel.target_object : rel.source_object)"
              title="Xem chi tiết đối tượng">
              {{ isSource(rel) ? rel.target_name : rel.source_name }}
            </span>

            <small>({{ $t(isSource(rel) ? rel.target_type : rel.source_type) }})</small>

          </span>
        </div>
        <button v-if="!disabled" class="btn-remove-rel" @click="removeRelation(rel.id)"
          title="Xóa liên kết">&times;</button>
      </div>
    </div>

    <!-- Modal xem chi tiết -->
    <ObjectDetailModal :objectId="viewingObjectId" :fieldDefinitions="allFields" @close="viewingObjectId = null" />

    <!-- Modal chọn đối tượng để liên kết -->
    <BaseModal :isOpen="showAddModal" title="Gán mối quan hệ mới" @close="closeModal">
      <div class="tabs-container">
        <div class="tab-button" :class="{ active: activeTab === 'internal' }" @click="activeTab = 'internal'">
          Trong hồ sơ này
        </div>
        <div class="tab-button" :class="{ active: activeTab === 'external' }" @click="activeTab = 'external'">
          Tìm kiếm toàn hệ thống
        </div>
      </div>

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
          
          <!-- Chế độ 1: Trong hồ sơ (Internal) -->
          <template v-if="activeTab === 'internal'">
            <div class="object-selector-list">
              <div v-for="obj in filteredPossibleTargets" :key="obj.id" class="selectable-object"
                :class="{ selected: selectedTargetId === obj.id }" @click="selectedTargetId = obj.id">
                <div class="obj-name">{{ obj.display_name }}</div>
              </div>
            </div>
            <div v-if="filteredPossibleTargets.length === 0" class="empty-list">
              Không tìm thấy đối tượng nào khác trong hồ sơ này.
            </div>
          </template>

          <!-- Chế độ 2: Toàn hệ thống (External) -->
          <template v-else>
            <div class="search-box">
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Tìm theo tên, CCCD, BKS..." 
                class="admin-form-control"
                @input="handleSearchInput"
              >
              <SvgIcon v-if="searching" name="loading" class="icon-spinning" />
            </div>

            <div class="object-selector-list search-results">
              <div v-for="obj in globalSearchResults" :key="obj.id" class="selectable-object"
                :class="{ selected: selectedTargetId === obj.id }" @click="selectedTargetId = obj.id">
                <div class="obj-name">{{ obj.display_name }}</div>
                <div class="obj-sub-info">
                  <span class="badge-type">{{ $t(obj.object_type) }}</span>
                  <span class="profile-context" v-if="obj.related_profiles && obj.related_profiles.length">
                    Hồ sơ gốc: {{ obj.related_profiles[0].name }}
                  </span>
                </div>
              </div>
              <div v-if="!searching && globalSearchResults.length === 0 && searchQuery" class="empty-list">
                Không tìm thấy kết quả phù hợp.
              </div>
              <div v-if="!searchQuery" class="empty-list">
                Nhập từ khóa để tìm kiếm (tối thiểu 2 ký tự)
              </div>
            </div>
          </template>
        </div>
      </div>

      <template #footer>
        <button class="btn-action btn-secondary" @click="closeModal">Hủy</button>
        <button class="btn-action btn-create" @click="confirmAddRelation" :disabled="!selectedTargetId">
          Xác nhận gán
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import MasterService from '@/services/master.service';
import MasterRelationService from '@/services/relation.service';
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
      viewingObjectId: null,

      // Cross-profile state
      activeTab: 'internal', // 'internal' | 'external'
      searchQuery: '',
      globalSearchResults: [],
      searching: false,
      searchTimeout: null,

      // === BƯỚC 1: ĐỊNH NGHĨA BẢN ĐỒ QUAN HỆ ===
      // Thêm đối tượng này vào data()
      relationTextMap: {
        'OWNER': {
          source: 'là chủ sở hữu của',    // Khi object hiện tại là nguồn (source)
          target: 'thuộc sở hữu của'      // Khi object hiện tại là đích (target)
        },
        'SECURES': {
          source: 'bảo đảm cho',
          target: 'được bảo đảm bởi'
        },
        'AMENDS': {
          source: 'bổ sung/sửa đổi cho',
          target: 'được bổ sung/sửa đổi bởi'
        },
        'REFERENCES': {
          source: 'dẫn chiếu đến',
          target: 'được dẫn chiếu bởi'
        },
        // Thêm các loại quan hệ khác ở đây trong tương lai
      }
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
        const res = await MasterService.getObjectById(this.masterObjectId);
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
      this.activeTab = 'internal';
      this.searchQuery = '';
      this.globalSearchResults = [];
    },
    handleSearchInput() {
      if (this.searchTimeout) clearTimeout(this.searchTimeout);
      
      const q = this.searchQuery.trim();
      if (q.length < 2) {
        this.globalSearchResults = [];
        return;
      }

      this.searchTimeout = setTimeout(async () => {
        this.searching = true;
        try {
          // Lưu ý: Có thể lọc theo objectType nếu cần thiết kế chặt chẽ hơn
          const res = await MasterService.searchMasterObjects(q);
          // Lọc bỏ chính nó nếu xuất hiện trong kết quả tìm kiếm
          this.globalSearchResults = res.data.filter(obj => obj.id !== this.masterObjectId);
        } catch (e) {
          console.error('Lỗi tìm kiếm đối tượng:', e);
        } finally {
          this.searching = false;
        }
      }, 500); // Debounce 500ms
    },
    async confirmAddRelation() {
      if (!this.selectedTargetId) return;
      try {
        await MasterRelationService.createRelation({
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
        await MasterRelationService.deleteRelation(relId);
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
    },
    // lựa chọn từ điển phù hợp với quan hệ
    getRelationDescription(rel) {
      const type = rel.relation_type;
      const map = this.relationTextMap[type];

      // Nếu có định nghĩa trong map, sử dụng nó
      if (map) {
        return this.isSource(rel) ? map.source : map.target;
      }

      // Nếu không, quay về mặc định để tránh lỗi
      return this.isSource(rel) ? 'có quan hệ với' : 'là quan hệ của';
    },
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

.rel-target strong.internal-obj-text {
  margin-left: 4px;
  color: #2c3e50; /* Màu tối hơn, không giống link */
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
  color: #b7950b !important;
  /* Màu vàng đậm (Dark Gold) cho dễ đọc trên nền trắng */
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  display: inline-block;
}
/* Hiệu ứng rõ ràng hơn khi hover để người dùng biết là click được */
.external-link:hover {
  color: #9a7d0a !important;
  text-decoration: underline !important;
  transform: translateY(-1px);
}

/* New Styles for Cross-profile Tabs */
.tabs-container {
  display: flex;
  border-bottom: 2px solid #edf2f7;
  margin-bottom: 20px;
}

.tab-button {
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 600;
  color: #718096;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab-button:hover {
  color: #4a5568;
  background: #f7fafc;
}

.tab-button.active {
  color: #3182ce;
  border-bottom-color: #3182ce;
}

.search-box {
  position: relative;
  margin-bottom: 15px;
}

.search-box .icon-spinning {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #3182ce;
}

.search-results {
  max-height: 250px !important;
}

.obj-sub-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.badge-type {
  font-size: 0.7em;
  background: #ebf8ff;
  color: #2b6cb0;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.profile-context {
  font-size: 0.75em;
  color: #718096;
  font-style: italic;
}
</style>

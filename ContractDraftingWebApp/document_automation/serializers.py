# Serializers for Document Automation App
# Chức năng: Chuyển đổi dữ liệu mô hình thành định dạng JSON và ngược lại
# Có vai trò giống như một cầu nối giữa các mô hình dữ liệu và các API endpoints
from rest_framework import serializers
from django.contrib.auth.models import User, Group, Permission
from .models import (
    Field, FieldGroup, LoanProfile, FieldValue, DocumentTemplate, 
    Role, FormView, UserProfile, MasterObject, LoanProfileObjectLink, MasterObjectType,
    MasterObjectRelation, AuditLog # ADDED
)

# 0. Serializer cho Role (MỚI)
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'description', 'relation_type', 'is_system']

# 0.0a Serializer cho Group và Permission (MỚI)
class PermissionSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

    def get_content_type(self, obj):
        if not obj.content_type:
            return "Khác"
        
        # Mapping tên Model sang Tiếng Việt thân thiện
        mapping = {
            'loanprofile': 'Hồ sơ vay',
            'loanprofileasset': 'Tài sản hồ sơ',
            'loanprofileperson': 'Người liên quan hồ sơ',
            'documenttemplate': 'Mẫu tài liệu',
            'field': 'Trường dữ liệu',
            'fieldgroup': 'Nhóm trường',
            'fieldvalue': 'Giá trị nhập liệu',
            'formview': 'Cấu hình giao diện',
            'masterobject': 'Đối tượng (Người/Tài sản)',
            'masterobjecttype': 'Loại đối tượng',
            'masterobjectrelation': 'Quan hệ đối tượng',
            'role': 'Vai trò',
            'user': 'Tài khoản người dùng',
            'group': 'Nhóm quyền',
            'userprofile': 'Thông tin mở rộng',
            'auditlog': 'Nhật ký hệ thống',
        }
        
        model_name = obj.content_type.model
        return mapping.get(model_name, f"Hệ thống: {model_name.capitalize()}")

class GroupSerializer(serializers.ModelSerializer):
    permissions_details = PermissionSerializer(source='permissions', many=True, read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permissions_details']

# 0.1 Serializer cho FormView (MỚI)
class FormViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormView
        fields = '__all__'

# 1.1 Serializer cho FieldGroup
class FieldGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldGroup
        fields = ['id', 'name', 'slug', 'order', 'note', 'allowed_forms', 'layout_position', 'allowed_object_types']

# 1.2 Serializer cho Field
class FieldSerializer(serializers.ModelSerializer):
    # Hiển thị tên nhóm thay vì chỉ ID
    group_name = serializers.CharField(source='group.name', read_only=True)
    group_slug = serializers.CharField(source='group.slug', read_only=True)
    group_layout_position = serializers.CharField(source='group.layout_position', read_only=True)
    # MỚI: Trả về danh sách object types mà group này áp dụng (thay thế group_object_type cũ)
    group_allowed_object_types = serializers.SerializerMethodField()
    # Đánh dấu đây có phải là field dựng sẵn từ model (không phải record trong bảng Field)
    is_model_field = serializers.BooleanField(read_only=True, default=False)

    def get_group_allowed_object_types(self, obj):
        if obj.group and obj.group.allowed_object_types.exists():
            return list(obj.group.allowed_object_types.values_list('code', flat=True))
        return []

    class Meta:
        model = Field
        fields = [
            'id', 'label', 'placeholder_key', 'data_type', 'group', 'group_name', 'group_slug', 'group_layout_position', 'group_allowed_object_types',
            'is_active', 'is_protected', 'use_digit_grouping', 'show_amount_in_words', 'default_value', 'note', 'is_model_field', 
            'order', 'width_cols', 'css_class', 'allowed_forms', 'allowed_object_types'
        ]


# 2.1 Serializer cho User (Nâng cấp)
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(source='profile.phone', required=False, allow_blank=True, allow_null=True)
    workplace = serializers.CharField(source='profile.workplace', required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(source='profile.department', required=False, allow_blank=True, allow_null=True)
    note = serializers.CharField(source='profile.note', required=False, allow_blank=True, allow_null=True)
    groups_details = GroupSerializer(source='groups', many=True, read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active', 'password', 'full_name', 'phone', 'workplace', 'department', 'note', 'groups', 'groups_details', 'permissions']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'read_only': True}
        }

    def get_permissions(self, obj):
        # Trả về danh sách codename của tất cả các quyền mà user có (bao gồm quyền từ Group)
        return list(obj.get_all_permissions())

    def update(self, instance, validated_data):
        # Tách dữ liệu profile (được source nén vào)
        profile_data = validated_data.pop('profile', {})
        
        # Cập nhật mật khẩu nếu có (thường Admin ít dùng qua update chung này)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Cập nhật Group nếu có
        groups = validated_data.pop('groups', None)
        if groups is not None:
            instance.groups.set(groups)

        # Cập nhật các trường User chính
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Cập nhật Profile gắn kèm
        profile, created = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        # Làm mới instance để serializer lấy được dữ liệu profile vừa lưu
        instance.refresh_from_db()
        return instance

# 2.2 Serializer cho Đăng ký (MỚI)
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    workplace = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'full_name', 'phone', 'workplace', 'department']

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        phone = validated_data.pop('phone', '')
        workplace = validated_data.pop('workplace', '')
        department = validated_data.pop('department', '')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        
        # Profile sẽ được tạo tự động qua Signal, ta chỉ cần cập nhật
        user.profile.full_name = full_name
        user.profile.phone = phone
        user.profile.workplace = workplace
        user.profile.department = department
        user.profile.save()

        # Tự động gán nhóm "soạn thảo" nếu có
        try:
            draft_group = Group.objects.filter(name='soạn thảo').first()
            if draft_group:
                user.groups.add(draft_group)
        except Exception:
            pass # Tránh lỗi làm đứt quãng quá trình đăng ký nếu có vấn đề về Group
        
        return user

# 2.3 Serializer cho Đổi mật khẩu (MỚI)
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu cũ không chính xác.")
        return value

# Person and Asset serializers removed






# 3. Serializer cho DocumentTemplate (Bắt buộc phải có)
class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'


# 4. Serializer cho LoanProfilePerson (Liên kết)
# LoanProfilePersonSerializer removed


# 5. Serializer cho FieldValue
class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)
    field_id = serializers.PrimaryKeyRelatedField(queryset=Field.objects.all(), source='field')

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'field_id', 'value', 'master_object']


# 6. Serializer cho LoanProfile
class LoanProfileSerializer(serializers.ModelSerializer):
    # Khai báo 3 trường tùy chỉnh mà Frontend cần
    field_values = serializers.SerializerMethodField()
    people = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()
    form_view_slug = serializers.CharField(source='form_view.slug', read_only=True)
    form_view_name = serializers.CharField(source='form_view.name', read_only=True)

    # Hiển thị tên người tạo thay vì ID
    created_by_user_name = serializers.CharField(source='created_by_user.username', read_only=True)

    class Meta:
        model = LoanProfile
        fields = [
            'id', 'name', 'status', 'created_at', 'updated_at', 'created_by_user_name', 
            'field_values', 'people', 'assets', 'form_view_slug', 'form_view_name'
        ]
        read_only_fields = ['created_at', 'updated_at']

    # Logic 1: Gom các FieldValue chung
    def get_field_values(self, obj):
        # Lấy tất cả giá trị trường của hồ sơ này mà master_object là Null
        fvs = obj.fieldvalue_set.filter(master_object__isnull=True)
        return {fv.field.placeholder_key: fv.value for fv in fvs}

    # Logic 2: Gom danh sách People (Universal filtered by PERSON)
    def get_people(self, obj):
        result = []
        # Filter Universal Links
        links = obj.object_links.filter(master_object__object_type='PERSON').select_related('master_object')
        
        for link in links:
            master = link.master_object
            # Get specific values for this profile
            specific_fvs = FieldValue.objects.filter(loan_profile=obj, master_object=master)
            fv_dict = {fv.field.placeholder_key: fv.value for fv in specific_fvs}
            
            # Helper to get value (Specific > Master > Empty)
            def get_val(key):
                if key in fv_dict: return fv_dict[key]
                # Fallback to Master data
                master_fv = FieldValue.objects.filter(master_object=master, field__placeholder_key=key, loan_profile__isnull=True).first()
                return master_fv.value if master_fv else ""

            # Standardize output for Frontend
            result.append({
                "id": master.id, 
                "ho_ten": get_val('ho_ten'),
                "cccd_so": get_val('cccd_so'),
                "roles": link.roles,
                "individual_field_values": fv_dict 
            })
        return result

    # Logic 3: Gom danh sách Assets (Tất cả đối tượng CÓ gán object_type và KHÔNG phải PERSON)
    def get_assets(self, obj):
        result = []
        links = obj.object_links.exclude(master_object__object_type='PERSON').select_related('master_object')
        
        for link in links:
            master = link.master_object
            # Get specific values
            specific_fvs = FieldValue.objects.filter(loan_profile=obj, master_object=master)
            asset_fv_dict = {fv.field.placeholder_key: fv.value for fv in specific_fvs}

            result.append({
                "id": master.id,
                "master_object": {
                    "object_type": master.object_type
                },
                "asset_field_values": asset_fv_dict,
                "roles": link.roles # Assets now support roles!
            })
        return result

# LoanProfileAssetSerializer removed

# 7. Serializers phục vụ Master Data (Quản lý tập trung)
# Legacy Master Data serializers removed


# --- UNIVERSAL ENTITY SERIALIZERS (New Architecture) ---

class MasterObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterObjectType
        fields = '__all__'

class MasterObjectSerializer(serializers.ModelSerializer):
    """Universal serializer for all entity types (Person, Asset, Savings, etc.)"""
    display_name = serializers.SerializerMethodField()
    last_updated_by_name = serializers.CharField(source='last_updated_by.username', read_only=True)
    profiles_count = serializers.SerializerMethodField()
    field_values = serializers.SerializerMethodField()
    object_type_display = serializers.SerializerMethodField()

    class Meta:
        model = MasterObject
        fields = [
            'id', 'object_type', 'object_type_display', 'display_name', 
            'created_at', 'updated_at', 'last_updated_by_name', 
            'created_at', 'updated_at', 'last_updated_by_name', 
            'profiles_count', 'field_values', 'related_assets', 'owners'
        ]
    
    # New fields for Relations
    related_assets = serializers.SerializerMethodField()
    owners = serializers.SerializerMethodField()

    def get_related_assets(self, obj):
        """Lấy danh sách tài sản mà đối tượng này sở hữu (relation_type=OWNER)"""
        # relations where source = obj
        rels = obj.relations_as_source.filter(relation_type='OWNER')
        return MasterObjectRelationSerializer(rels, many=True).data

    def get_owners(self, obj):
        """Lấy danh sách chủ sở hữu của tài sản này"""
        # relations where target = obj
        rels = obj.relations_as_target.filter(relation_type='OWNER')
        return MasterObjectRelationSerializer(rels, many=True).data

    def get_display_name(self, obj):
        """Ưu tiên lấy giá trị của trường định danh (identity_field_key)"""
        try:
            from .models import MasterObjectType, FieldValue
            # 1. Lấy cấu hình identity_field_key của loại đối tượng này
            obj_type = MasterObjectType.objects.filter(code=obj.object_type).first()
            id_key = obj_type.identity_field_key if obj_type else None
            
            # 2. Nếu có cấu hình id_key, tìm giá trị của nó
            if id_key:
                # Tìm trong Master data (loan_profile=null)
                fv = FieldValue.objects.filter(master_object=obj, field__placeholder_key=id_key, loan_profile__isnull=True).first()
                if fv and fv.value:
                    return fv.value
            
            # 3. Fallback logic cũ nếu không có cấu hình hoặc cấu hình không có giá trị
            key = 'ho_ten' if obj.object_type == 'PERSON' else 'so_giay_chung_nhan'
            fv = FieldValue.objects.filter(master_object=obj, field__placeholder_key=key, loan_profile__isnull=True).first()
            if fv and fv.value:
                return fv.value
            
            # 4. Fallback cuối cùng nếu không có bất cứ data nào: Tên loại #ID
            stype = self.get_object_type_display(obj)
            return f"{stype} #{obj.id}"
        except Exception:
            return f"Object #{obj.id}"
    
    def get_object_type_display(self, obj):
        """Get display name for object type from MasterObjectType"""
        try:
            obj_type = MasterObjectType.objects.get(code=obj.object_type)
            return obj_type.name
        except MasterObjectType.DoesNotExist:
            return obj.object_type

    def get_profiles_count(self, obj):
        return obj.profile_links.count()

    def get_field_values(self, obj):
        """Return all canonical field values for this object"""
        fvs = FieldValue.objects.filter(master_object=obj, loan_profile__isnull=True)
        return {fv.field.placeholder_key: fv.value for fv in fvs}

# 8. Serializer cho Relation (MỚI)
class MasterObjectRelationSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source_object.display_name', read_only=True) # Reuse logic from MO
    target_name = serializers.CharField(source='target_object.display_name', read_only=True)
    target_type = serializers.CharField(source='target_object.object_type', read_only=True)
    source_type = serializers.CharField(source='source_object.object_type', read_only=True)

    class Meta:
        model = MasterObjectRelation
        fields = ['id', 'source_object', 'target_object', 'relation_type', 'created_at', 
                  'source_name', 'target_name', 'target_type', 'source_type']


class LoanProfileObjectLinkSerializer(serializers.ModelSerializer):
    """Serializer for profile-object links with roles"""
    object = MasterObjectSerializer(source='master_object', read_only=True)
    master_object_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LoanProfileObjectLink
        fields = ['id', 'loan_profile', 'master_object_id', 'object', 'roles']

# 9. Serializer cho Audit Log (MỚI)
class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.profile.full_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'

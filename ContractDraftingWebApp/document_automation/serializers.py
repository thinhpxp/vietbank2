# Serializers for Document Automation App
# Chức năng: Chuyển đổi dữ liệu mô hình thành định dạng JSON và ngược lại
# Có vai trò giống như một cầu nối giữa các mô hình dữ liệu và các API endpoints
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Field, FieldGroup, LoanProfile, FieldValue, DocumentTemplate, 
    Role, FormView, UserProfile, MasterObject, LoanProfileObjectLink, MasterObjectType
)

# 0. Serializer cho Role (MỚI)
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

# 0.1 Serializer cho FormView (MỚI)
class FormViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormView
        fields = '__all__'

# 1.1 Serializer cho FieldGroup (MỚI)
class FieldGroupSerializer(serializers.ModelSerializer):
    object_type_code = serializers.CharField(source='object_type.code', read_only=True, allow_null=True)
    
    class Meta:
        model = FieldGroup
        fields = ['id', 'name', 'slug', 'order', 'note', 'allowed_forms', 'layout_position', 'allowed_object_types', 'object_type', 'object_type_code'] # Added allowed_object_types'] # Added layout_position

# 1.2 Serializer cho Field
class FieldSerializer(serializers.ModelSerializer):
    # Hiển thị tên nhóm thay vì chỉ ID
    group_name = serializers.CharField(source='group.name', read_only=True)
    group_slug = serializers.CharField(source='group.slug', read_only=True)
    group_layout_position = serializers.CharField(source='group.layout_position', read_only=True) # MỚI: Trả về vị trí hiển thị
    group_object_type = serializers.CharField(source='group.object_type.code', read_only=True, allow_null=True) # MỚI: Trả về vị trí hiển thị
    # Đánh dấu đây có phải là field dựng sẵn từ model (không phải record trong bảng Field)
    is_model_field = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Field
        fields = [
            'id', 'label', 'placeholder_key', 'data_type', 'group', 'group_name', 'group_slug', 'group_layout_position', 'group_object_type',
            'is_active', 'is_protected', 'use_digit_grouping', 'show_amount_in_words', 'default_value', 'note', 'is_model_field', 
            'order', 'width_cols', 'css_class', 'allowed_forms', 'allowed_object_types'
        ]


# 2.1 Serializer cho User (MỚI - Để quản lý End-user)
class UserSerializer(serializers.ModelSerializer):
    # Lấy note từ bảng UserProfile liên kết
    note = serializers.CharField(source='profile.note', required=False, allow_blank=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active', 'password', 'note']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Tách note ra khỏi dữ liệu user
        note_data = validated_data.pop('profile', {}).get('note', '')
        user = User.objects.create_user(**validated_data)
        # Cập nhật note vào profile (đã được tạo tự động bởi Signal)
        user.profile.note = note_data
        user.profile.save()
        return user

    def update(self, instance, validated_data):
        # Tách note ra khỏi dữ liệu user
        note_data = validated_data.pop('profile', {}).get('note', None)

        # Cập nhật mật khẩu nếu có
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        # Cập nhật các trường khác của User
        instance = super().update(instance, validated_data)

        # Cập nhật note nếu có
        if note_data is not None:
            instance.profile.note = note_data
            instance.profile.save()

        return instance

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
            'id', 'name', 'created_at', 'updated_at', 'created_by_user_name', 
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
            'profiles_count', 'field_values'
        ]

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


class LoanProfileObjectLinkSerializer(serializers.ModelSerializer):
    """Serializer for profile-object links with roles"""
    object = MasterObjectSerializer(source='master_object', read_only=True)
    master_object_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LoanProfileObjectLink
        fields = ['id', 'loan_profile', 'master_object_id', 'object', 'roles']

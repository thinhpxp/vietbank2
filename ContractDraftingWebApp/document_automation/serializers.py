# Serializers for Document Automation App
# Chức năng: Chuyển đổi dữ liệu mô hình thành định dạng JSON và ngược lại
# Có vai trò giống như một cầu nối giữa các mô hình dữ liệu và các API endpoints
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Field, FieldGroup, LoanProfile, Person, LoanProfilePerson, 
    FieldValue, DocumentTemplate, UserProfile, Role, Asset, 
    LoanProfileAsset, FormView
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
    class Meta:
        model = FieldGroup
        fields = ['id', 'name', 'order', 'note', 'allowed_forms']

# 1.2 Serializer cho Field
class FieldSerializer(serializers.ModelSerializer):
    # Hiển thị tên nhóm thay vì chỉ ID
    group_name = serializers.CharField(source='group.name', read_only=True)
    # Đánh dấu đây có phải là field dựng sẵn từ model (không phải record trong bảng Field)
    is_model_field = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Field
        fields = [
            'id', 'label', 'placeholder_key', 'data_type', 'group', 'group_name', 
            'is_active', 'is_protected', 'use_digit_grouping', 'show_amount_in_words', 'default_value', 'note', 'is_model_field', 
            'order', 'width_cols', 'css_class', 'allowed_forms'
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

# 2.2 Serializer cho Person
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


# --- MỚI: Serializer cho Asset ---
class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'






# 3. Serializer cho DocumentTemplate (Bắt buộc phải có)
class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'


# 4. Serializer cho LoanProfilePerson (Liên kết)
class LoanProfilePersonSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)

    class Meta:
        model = LoanProfilePerson
        fields = '__all__'


# 5. Serializer cho FieldValue
class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)
    field_id = serializers.PrimaryKeyRelatedField(queryset=Field.objects.all(), source='field')

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'field_id', 'value', 'person']


# 6. Serializer cho LoanProfile
class LoanProfileSerializer(serializers.ModelSerializer):
    # Khai báo 3 trường tùy chỉnh mà Frontend cần
    field_values = serializers.SerializerMethodField()
    people = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField() # Mới: Field cho tài sản
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

    # Logic 1: Gom các FieldValue chung (không thuộc về Person nào)
    def get_field_values(self, obj):
        # Lấy tất cả giá trị trường của hồ sơ này mà person là Null
        fvs = obj.fieldvalue_set.filter(person__isnull=True)
        # Chuyển thành Dict: { "so_tien_vay": "1 tỷ", "thoi_han": "12" }
        return {fv.field.placeholder_key: fv.value for fv in fvs}

    # Logic 2: Gom danh sách People và FieldValue riêng của họ
    def get_people(self, obj):
        result = []
        # Lấy danh sách liên kết (sử dụng related_name='linked_people' đã định nghĩa trong Models)
        # Nếu chưa có related_name, dùng loanprofileperson_set.all()
        linked_people = obj.linked_people.select_related('person').all()

        for link in linked_people:
            person = link.person

            # Lấy các giá trị trường riêng của người này trong hồ sơ này
            person_fvs = obj.fieldvalue_set.filter(person=person)
            individual_fv_dict = {fv.field.placeholder_key: fv.value for fv in person_fvs}

            # [REFACTOR] Đảm bảo ho_ten và cccd_so luôn có trong dict này để frontend hiển thị
            # Trước đây fallback vào column, giờ chỉ dựa vào FieldValue (đã được lưu khi save form)
            if 'ho_ten' not in individual_fv_dict:
                individual_fv_dict['ho_ten'] = ""
            if 'cccd_so' not in individual_fv_dict:
                 individual_fv_dict['cccd_so'] = ""

            result.append({
                "id": person.id,  # QUAN TRỌNG: ID để biết là người cũ khi sửa
                "ho_ten": individual_fv_dict.get('ho_ten', ''),
                "cccd_so": individual_fv_dict.get('cccd_so', ''),
                "roles": link.roles,  # Lấy mảng roles từ bảng trung gian
                "individual_field_values": individual_fv_dict  # Các trường động riêng
            })

        return result

    # Logic 3: Gom danh sách Assets và FieldValue riêng của chúng
    def get_assets(self, obj):
        result = []
        linked_assets = obj.linked_assets.select_related('asset').all()

        for link in linked_assets:
            asset = link.asset
            # Lấy các giá trị trường riêng của tài sản này
            asset_fvs = obj.fieldvalue_set.filter(asset=asset)
            asset_fv_dict = {fv.field.placeholder_key: fv.value for fv in asset_fvs}

            result.append({
                "id": asset.id,
                "asset_field_values": asset_fv_dict
            })
        
        return result
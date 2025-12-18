# Serializers for Document Automation App
# Chức năng: Chuyển đổi dữ liệu mô hình thành định dạng JSON và ngược lại
# Có vai trò giống như một cầu nối giữa các mô hình dữ liệu và các API endpoints
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Field, FieldGroup, LoanProfile, Person, LoanProfilePerson, FieldValue, DocumentTemplate, UserProfile

# 1.1 Serializer cho FieldGroup (MỚI)
class FieldGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldGroup
        fields = ['id', 'name', 'order', 'note']

# 1.2 Serializer cho Field
class FieldSerializer(serializers.ModelSerializer):
    # Hiển thị tên nhóm thay vì chỉ ID
    group_name = serializers.CharField(source='group.name', read_only=True)
    # Đánh dấu đây có phải là field dựng sẵn từ model (không phải record trong bảng Field)
    is_model_field = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Field
        fields = ['id', 'label', 'placeholder_key', 'data_type', 'group', 'group_name', 'is_active', 'note', 'is_model_field']


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
    # Khai báo 2 trường tùy chỉnh mà Frontend cần
    field_values = serializers.SerializerMethodField()
    people = serializers.SerializerMethodField()

    # Hiển thị tên người tạo thay vì ID
    created_by_user_name = serializers.CharField(source='created_by_user.username', read_only=True)

    class Meta:
        model = LoanProfile
        fields = ['id', 'name', 'created_at', 'updated_at', 'created_by_user_name', 'field_values', 'people']
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

            result.append({
                "id": person.id,  # QUAN TRỌNG: ID để biết là người cũ khi sửa
                "ho_ten": person.name_for_display,
                "cccd_so": person.cccd_so,
                "roles": link.roles,  # Lấy mảng roles từ bảng trung gian
                "individual_field_values": individual_fv_dict  # Các trường động riêng
            })

        return result
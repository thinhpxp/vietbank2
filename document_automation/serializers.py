from rest_framework import serializers
from .models import Field, LoanProfile, Person, LoanProfilePerson, FieldValue, DocumentTemplate
from django.contrib.auth.models import User


# Serializer cho Field (định nghĩa trường dữ liệu)
class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'


# Serializer cho Person (người liên quan)
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'  # Hoặc chỉ các trường bạn muốn hiển thị/nhập


# Serializer cho LoanProfilePerson (liên kết hồ sơ và người)
class LoanProfilePersonSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)  # Để hiển thị thông tin người liên quan

    # Nếu muốn tạo/cập nhật liên kết người, có thể cần `person_id = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all(), source='person')`
    class Meta:
        model = LoanProfilePerson
        fields = '__all__'


# Serializer cho FieldValue (giá trị của trường)
class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)  # Để hiển thị thông tin trường
    field_id = serializers.PrimaryKeyRelatedField(queryset=Field.objects.all(),
                                                  source='field')  # Để gửi field_id khi tạo/cập nhật

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'field_id', 'value', 'person']  # 'person' có thể null


# Serializer cho LoanProfile (Hồ sơ Vay) - có thể bao gồm các trường con
class LoanProfileSerializer(serializers.ModelSerializer):
    # Nested serializer để hiển thị các giá trị trường và người liên quan cùng lúc
    field_values = FieldValueSerializer(source='fieldvalue_set', many=True, read_only=True)
    loan_profile_people = LoanProfilePersonSerializer(source='loanprofileperson_set', many=True, read_only=True)
    created_by_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='created_by_user',
                                                            write_only=True, required=False)  # Cho phép gửi user_id
    created_by_user_name = serializers.CharField(source='created_by_user.username',
                                                 read_only=True)  # Để hiển thị tên người tạo

    class Meta:
        model = LoanProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    # Custom create/update method nếu cần xử lý phức tạp khi lưu field_values, people
    def create(self, validated_data):
        # Xử lý logic tạo LoanProfile và các FieldValue/Person liên quan
        # Đây là nơi phức tạp nhất, sẽ cần logic để tạo Person nếu chưa có,
        # tạo FieldValue, LoanProfilePerson.
        # Để đơn giản, ban đầu có thể chỉ tạo LoanProfile
        user = self.context['request'].user if 'request' in self.context else None
        if user and user.is_authenticated:
            validated_data['created_by_user'] = user

        # Xóa created_by_user_id khỏi validated_data nếu có, vì nó đã được xử lý
        if 'created_by_user_id' in validated_data:
            del validated_data['created_by_user_id']

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Xử lý logic cập nhật
        return super().update(instance, validated_data)


# Serializer cho DocumentTemplate
class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Field, LoanProfile, Person, LoanProfilePerson, FieldValue, DocumentTemplate


# 1. Serializer cho Field
class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'


# 2. Serializer cho Person
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
    # Nested serializer để hiển thị dữ liệu con
    field_values = FieldValueSerializer(source='fieldvalue_set', many=True, read_only=True)
    linked_people = LoanProfilePersonSerializer(source='loanprofileperson_set', many=True,
                                                read_only=True)  # Lưu ý: source khớp với related_name trong models

    created_by_user_name = serializers.CharField(source='created_by_user.username', read_only=True)

    class Meta:
        model = LoanProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by_user']
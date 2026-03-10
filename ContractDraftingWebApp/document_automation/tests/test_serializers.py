import pytest
from django.contrib.auth.models import User
from document_automation.models import MasterObject, MasterObjectType, Field, FieldGroup, FieldValue, LoanProfile, LoanProfileObjectLink
from document_automation.master_object_serializer import MasterObjectSerializer

@pytest.mark.django_db
class TestMasterObjectSerializer:
    @pytest.fixture
    def setup_data(self):
        # Create User
        user = User.objects.create_user(username='testuser', password='password')
        
        # Create Object Type
        obj_type = MasterObjectType.objects.create(
            code='PERSON', 
            name='Cá nhân', 
            identity_field_key='ho_ten'
        )
        
        # Create Field Group & Fields
        group = FieldGroup.objects.create(name='Cơ bản', entity_type='PERSON')
        field_name = Field.objects.create(label='Họ tên', placeholder_key='ho_ten', group=group)
        field_phone = Field.objects.create(label='Số điện thoại', placeholder_key='so_dien_thoai', group=group)
        
        # Create Master Object
        obj = MasterObject.objects.create(object_type='PERSON', last_updated_by=user)
        
        # Create Field Values (Master Data)
        FieldValue.objects.create(master_object=obj, field=field_name, value='Nguyễn Văn A')
        FieldValue.objects.create(master_object=obj, field=field_phone, value='0909123456')
        
        # Create Loan Profile & Link
        profile = LoanProfile.objects.create(name='Hồ sơ Test', created_by_user=user)
        LoanProfileObjectLink.objects.create(loan_profile=profile, master_object=obj, roles=['Chủ tài sản'])
        
        return {
            'user': user,
            'obj': obj,
            'profile': profile,
            'field_name': field_name,
            'field_phone': field_phone
        }

    def test_display_name_person(self, setup_data):
        """Kiểm tra display_name lấy từ ho_ten cho loại PERSON."""
        serializer = MasterObjectSerializer(instance=setup_data['obj'])
        assert serializer.data['display_name'] == 'Nguyễn Văn A'

    def test_field_values_only_master(self, setup_data):
        """Kiểm tra field_values chỉ lấy dữ liệu gốc (không lấy dữ liệu theo hồ sơ)."""
        # Tạo thêm data rác theo hồ sơ (shadow data)
        FieldValue.objects.create(
            master_object=setup_data['obj'], 
            loan_profile=setup_data['profile'], 
            field=setup_data['field_name'], 
            value='Tên khác trong hồ sơ'
        )
        
        serializer = MasterObjectSerializer(instance=setup_data['obj'])
        values = serializer.data['field_values']
        
        # Phải vẫn là Nguyễn Văn A vì Serializer chỉ lấy loan_profile__isnull=True
        assert values['ho_ten'] == 'Nguyễn Văn A'
        assert values['so_dien_thoai'] == '0909123456'

    def test_profiles_count(self, setup_data):
        """Kiểm tra đếm số hồ sơ liên kết."""
        serializer = MasterObjectSerializer(instance=setup_data['obj'])
        assert serializer.data['profiles_count'] == 1
        
        # Thêm 1 hồ sơ nữa
        p2 = LoanProfile.objects.create(name='Hồ sơ 2')
        LoanProfileObjectLink.objects.create(loan_profile=p2, master_object=setup_data['obj'])
        
        serializer = MasterObjectSerializer(instance=setup_data['obj'])
        assert serializer.data['profiles_count'] == 2

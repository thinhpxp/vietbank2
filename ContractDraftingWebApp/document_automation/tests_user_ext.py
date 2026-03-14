from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from document_automation.models import MasterObjectType, MasterObject, FieldGroup, Field

class UserExtensionProtectionTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'password123')
        self.client.force_login(self.admin_user)
        
        # Create a protected object type
        self.obj_type = MasterObjectType.objects.create(
            code='USER_EXT', 
            name='User Extension', 
            is_system=True
        )
        
        # Create a protected field group
        self.group = FieldGroup.objects.create(
            name='System Info', 
            entity_type='USER_EXT', 
            is_protected=True
        )

    def test_delete_protected_object_type_fails(self):
        url = reverse('masterobjecttype-detail', kwargs={'pk': self.obj_type.pk})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert MasterObjectType.objects.filter(code='USER_EXT').exists()

    def test_delete_protected_group_fails(self):
        url = reverse('fieldgroup-detail', kwargs={'pk': self.group.pk})
        response = self.client.delete(url)
        # Assuming the viewset handles this and returns 400 or 403
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]
        assert FieldGroup.objects.filter(pk=self.group.pk).exists()

class UserExtensionVisibilityTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin_vis', 'admin@test.com', 'password123')
        self.client.force_login(self.admin_user)
        
        # Create a USER_EXT object
        self.user_obj = MasterObject.objects.create(
            object_type='USER_EXT'
        )
        # Create a normal ASSET object
        self.asset_obj = MasterObject.objects.create(
            object_type='ASSET'
        )

    def test_master_data_excludes_user_ext(self):
        url = reverse('master-objects-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Should only see ASSET, not USER_EXT
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
        else:
            results = data
            
        ids = [item['id'] for item in results]
        assert self.asset_obj.id in ids
        assert self.user_obj.id not in ids

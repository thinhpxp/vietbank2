
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from document_automation.models import MasterObjectType, MasterObject, MasterObjectRelation

class ObjectRelationWhitelistTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'password123')
        self.client.force_login(self.admin_user)
        
        # Tạo các loại đối tượng
        self.type_a = MasterObjectType.objects.create(code='ALPHA', name='Alpha Type', allow_relations=True, is_restricted=True)
        self.type_b = MasterObjectType.objects.create(code='BETA', name='Beta Type', allow_relations=True, is_restricted=False)
        self.type_c = MasterObjectType.objects.create(code='GAMMA', name='Gamma Type', allow_relations=True, is_restricted=False)
        
        # Thiết lập Whitelist: ALPHA chỉ được liên kết với BETA
        self.type_a.allowed_relation_types.add(self.type_b)
        
        # Tạo các đối tượng thực tế
        self.obj_alpha = MasterObject.objects.create(object_type='ALPHA')
        self.obj_beta = MasterObject.objects.create(object_type='BETA')
        self.obj_gamma = MasterObject.objects.create(object_type='GAMMA')

    def test_restricted_target_violation(self):
        """Kiểm tra: GAMMA không thể liên kết tới ALPHA vì ALPHA bị restricted và GAMMA không có trong whitelist của ALPHA"""
        url = reverse('masterobjectrelation-create-relation')
        data = {
            "source_id": self.obj_gamma.id,
            "target_id": self.obj_alpha.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], "WHITELIST_VIOLATION_TARGET")

    def test_whitelist_violation(self):
        """Kiểm tra: ALPHA chỉ được liên kết tới BETA. Nếu ALPHA liên kết tới GAMMA -> Vi phạm Whitelist."""
        url = reverse('masterobjectrelation-create-relation')
        data = {
            "source_id": self.obj_alpha.id,
            "target_id": self.obj_gamma.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], "WHITELIST_VIOLATION_SOURCE")

    def test_successful_relation(self):
        """Kiểm tra: ALPHA liên kết tới BETA -> Hợp lệ (BETA nằm trong whitelist của ALPHA)."""
        url = reverse('masterobjectrelation-create-relation')
        data = {
            "source_id": self.obj_alpha.id,
            "target_id": self.obj_beta.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(MasterObjectRelation.objects.filter(source_object=self.obj_alpha, target_object=self.obj_beta).exists())

    def test_public_to_public(self):
        """Kiểm tra: BETA liên kết tới GAMMA -> Hợp lệ (Cả 2 đều public)."""
        url = reverse('masterobjectrelation-create-relation')
        data = {
            "source_id": self.obj_beta.id,
            "target_id": self.obj_gamma.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from document_automation.models import MasterObjectType, MasterObject, MasterObjectRelation

@pytest.mark.django_db
class TestObjectRelationWhitelist:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='admin_test', password='password', email='test@example.com')
        self.client.force_authenticate(user=self.user)
        
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
        """Kiểm tra: GAMMA không thể liên kết tới ALPHA vì ALPHA bị restricted và GAMMA không có trong whitelist của ALPHA (vậy ALPHA không có trong whitelist của GAMMA)"""
        # Lưu ý: Theo logic code: Nếu Target (ALPHA) bị restricted, Source (GAMMA) phải có Target trong whitelist.
        # Ở đây GAMMA whitelist trống, nên không thể liên kết tới bất kỳ Restricted target nào.
        url = "/api/master-relations/create_relation/"
        data = {
            "source_id": self.obj_gamma.id,
            "target_id": self.obj_alpha.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 403
        assert response.data['code'] == "RESTRICTED_TARGET"

    def test_whitelist_violation(self):
        """Kiểm tra: ALPHA chỉ được liên kết tới BETA. Nếu ALPHA liên kết tới GAMMA -> Vi phạm Whitelist."""
        url = "/api/master-relations/create_relation/"
        data = {
            "source_id": self.obj_alpha.id,
            "target_id": self.obj_gamma.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 403
        assert response.data['code'] == "WHITELIST_VIOLATION"

    def test_successful_relation(self):
        """Kiểm tra: ALPHA liên kết tới BETA -> Hợp lệ (BETA nằm trong whitelist của ALPHA)."""
        url = "/api/master-relations/create_relation/"
        data = {
            "source_id": self.obj_alpha.id,
            "target_id": self.obj_beta.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        assert MasterObjectRelation.objects.filter(source_object=self.obj_alpha, target_object=self.obj_beta).exists()

    def test_public_to_public(self):
        """Kiểm tra: BETA liên kết tới GAMMA -> Hợp lệ (Cả 2 đều public)."""
        url = "/api/master-relations/create_relation/"
        data = {
            "source_id": self.obj_beta.id,
            "target_id": self.obj_gamma.id,
            "relation_type": "OWNER"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200

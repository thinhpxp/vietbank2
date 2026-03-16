from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from document_automation.models import MasterObject, MasterObjectRelation

class BranchAttorneyFilterTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'password123')
        self.client.force_login(self.admin_user)
        
        # 1. Create Branches
        self.branch_a = MasterObject.objects.create(object_type='BRANCH')
        self.branch_b = MasterObject.objects.create(object_type='BRANCH')
        
        # 2. Create Attorneys
        self.attorney_1 = MasterObject.objects.create(object_type='ATTORNEY')
        self.attorney_2 = MasterObject.objects.create(object_type='ATTORNEY')
        self.attorney_3 = MasterObject.objects.create(object_type='ATTORNEY')
        
        # 3. Create Relations (REPRESENTATIVE)
        # Attorney 1 belongs to Branch A
        MasterObjectRelation.objects.create(
            source_object=self.branch_a,
            target_object=self.attorney_1,
            relation_type='REPRESENTATIVE'
        )
        # Attorney 2 belongs to Branch B
        MasterObjectRelation.objects.create(
            source_object=self.branch_b,
            target_object=self.attorney_2,
            relation_type='REPRESENTATIVE'
        )
        # Attorney 3 is independent (no relation)

    def test_filter_attorney_by_branch_a(self):
        url = reverse('master-objects-list')
        params = {
            'object_type': 'ATTORNEY',
            'related_to_source': self.branch_a.id,
            'relation_type': 'REPRESENTATIVE'
        }
        response = self.client.get(url, data=params)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
        else:
            results = data
            
        ids = [item['id'] for item in results]
        
        # Branch A should only have Attorney 1
        assert self.attorney_1.id in ids
        assert self.attorney_2.id not in ids
        assert self.attorney_3.id not in ids
        assert len(ids) == 1

    def test_filter_attorney_by_branch_b(self):
        url = reverse('master-objects-list')
        params = {
            'object_type': 'ATTORNEY',
            'related_to_source': self.branch_b.id,
            'relation_type': 'REPRESENTATIVE'
        }
        response = self.client.get(url, data=params)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        ids = [item['id'] for item in results]
        
        # Branch B should only have Attorney 2
        assert self.attorney_2.id in ids
        assert self.attorney_1.id not in ids
        assert self.attorney_3.id not in ids
        assert len(ids) == 1

    def test_no_filter_returns_all_attorneys(self):
        url = reverse('master-objects-list')
        params = {'object_type': 'ATTORNEY'}
        response = self.client.get(url, data=params)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        ids = [item['id'] for item in results]
        
        # Without relation filter, should see all 3
        assert self.attorney_1.id in ids
        assert self.attorney_2.id in ids
        assert self.attorney_3.id in ids
        assert len(ids) >= 3

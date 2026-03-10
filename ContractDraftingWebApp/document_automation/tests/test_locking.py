import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from document_automation.models import MasterObject, LoanProfile, MasterObjectType
from django.utils import timezone
from datetime import timedelta

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user1(db):
    return User.objects.create_user(username='user1', password='password1')

@pytest.fixture
def user2(db):
    return User.objects.create_user(username='user2', password='password1')

@pytest.fixture
def master_object(db):
    obj_type = MasterObjectType.objects.create(code='PERSON', name='Cá nhân')
    return MasterObject.objects.create(object_type='PERSON')

@pytest.fixture
def loan_profile(db, user1):
    return LoanProfile.objects.create(name="Test Profile", created_by=user1)

@pytest.mark.django_db
class TestLockingDiscovery:
    
    def test_master_object_locking_flow(self, api_client, user1, user2, master_object):
        """Kiểm tra luồng lock của MasterObject giữa 2 user."""
        url = reverse('master-objects-acquire-lock', kwargs={'pk': master_object.id})
        
        # 1. User 1 lấy lock -> Thành công
        api_client.force_authenticate(user=user1)
        response = api_client.post(url)
        assert response.status_code == 200
        assert response.data['locked'] is False
        
        # Kiểm tra DB
        master_object.refresh_from_db()
        assert master_object.editing_by == user1
        
        # 2. User 2 cố gắng lấy lock -> Thất bại (423 Locked)
        api_client.force_authenticate(user=user2)
        response = api_client.post(url)
        assert response.status_code == 423
        assert response.data['locked'] is True
        assert response.data['locked_by'] == 'user1'
        
        # 3. User 1 release lock -> Thành công
        api_client.force_authenticate(user=user1)
        release_url = reverse('master-objects-release-lock', kwargs={'pk': master_object.id})
        response = api_client.post(release_url)
        assert response.status_code == 200
        
        master_object.refresh_from_db()
        assert master_object.editing_by is None
        
        # 4. User 2 lấy lock sau khi đã được giải phóng -> Thành công
        api_client.force_authenticate(user=user2)
        response = api_client.post(url)
        assert response.status_code == 200
        assert response.data['locked'] is False
        
        master_object.refresh_from_db()
        assert master_object.editing_by == user2

    def test_loan_profile_locking_flow(self, api_client, user1, user2, loan_profile):
        """Kiểm tra luồng lock của LoanProfile giữa 2 user."""
        url = reverse('loan-profile-acquire-lock', kwargs={'pk': loan_profile.id})
        
        # 1. User 1 lấy lock
        api_client.force_authenticate(user=user1)
        response = api_client.post(url)
        assert response.status_code == 200
        
        # 2. User 2 cố gắng lấy lock -> 423
        api_client.force_authenticate(user=user2)
        response = api_client.post(url)
        assert response.status_code == 423
        assert response.data['locked_by'] == 'user1'

    def test_lock_expiration(self, api_client, user1, user2, master_object):
        """Kiểm tra việc tự động giải phóng lock sau 15 phút."""
        # Giả lập lock đã tồn tại từ 20 phút trước
        master_object.editing_by = user1
        master_object.editing_since = timezone.now() - timedelta(seconds=901)
        master_object.save()
        
        # User 2 cố gắng lấy lock -> Phải thành công vì lock cũ đã hết hạn
        api_client.force_authenticate(user=user2)
        url = reverse('master-objects-acquire-lock', kwargs={'pk': master_object.id})
        response = api_client.post(url)
        
        assert response.status_code == 200
        assert response.data['locked'] is False
        
        master_object.refresh_from_db()
        assert master_object.editing_by == user2

    def test_heartbeat_updates_timer(self, api_client, user1, master_object):
        """Kiểm tra heartbeat cập nhật thời gian lock."""
        master_object.editing_by = user1
        old_time = timezone.now() - timedelta(minutes=5)
        master_object.editing_since = old_time
        master_object.save()
        
        api_client.force_authenticate(user=user1)
        url = reverse('master-objects-heartbeat', kwargs={'pk': master_object.id})
        response = api_client.post(url)
        
        assert response.status_code == 200
        master_object.refresh_from_db()
        assert master_object.editing_since > old_time

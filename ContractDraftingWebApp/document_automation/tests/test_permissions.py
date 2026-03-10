import pytest
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIRequestFactory
from document_automation.permissions import IsAdminOrManager, ReadOnlyMetadataOrAdmin, IsSuperUser
from document_automation.models import MasterObject

@pytest.mark.django_db
class TestPermissions:
    
    @pytest.fixture
    def factory(self):
        return APIRequestFactory()

    @pytest.fixture
    def superuser(self):
        return User.objects.create_superuser(username='admin', password='password', email='admin@test.com')

    @pytest.fixture
    def staff_user(self):
        user = User.objects.create_user(username='staff', password='password', is_staff=True)
        # Add to group with view permissions
        group = Group.objects.create(name='Managers')
        content_type = ContentType.objects.get_for_model(MasterObject)
        permission = Permission.objects.get(codename='view_masterobject', content_type=content_type)
        group.permissions.add(permission)
        user.groups.add(group)
        return user

    @pytest.fixture
    def regular_user(self):
        return User.objects.create_user(username='user', password='password')

    # --- IsAdminOrManager ---
    def test_is_admin_or_manager_superuser(self, factory, superuser):
        request = factory.get('/')
        request.user = superuser
        permission = IsAdminOrManager()
        assert permission.has_permission(request, None) is True

    def test_is_admin_or_manager_regular_denied(self, factory, regular_user):
        request = factory.get('/')
        request.user = regular_user
        permission = IsAdminOrManager()
        # Should be false because regular user has no django model perms for the view
        # We need a dummy view with a queryset to trigger DjangoModelPermissions logic if needed,
        # but here the hardcoded superuser check happens first.
        # Since it's not superuser, it calls super().has_permission
        assert permission.has_permission(request, type('View', (), {'queryset': MasterObject.objects.all()})) is False

    # --- ReadOnlyMetadataOrAdmin ---
    def test_read_only_metadata_get_allowed(self, factory, regular_user):
        request = factory.get('/')
        request.user = regular_user
        permission = ReadOnlyMetadataOrAdmin()
        assert permission.has_permission(request, None) is True

    def test_read_only_metadata_post_denied_regular(self, factory, regular_user):
        request = factory.post('/')
        request.user = regular_user
        permission = ReadOnlyMetadataOrAdmin()
        assert permission.has_permission(request, None) is False

    def test_read_only_metadata_post_allowed_superuser(self, factory, superuser):
        request = factory.post('/')
        request.user = superuser
        permission = ReadOnlyMetadataOrAdmin()
        assert permission.has_permission(request, None) is True

    # --- IsSuperUser ---
    def test_is_superuser_allowed(self, factory, superuser):
        request = factory.get('/')
        request.user = superuser
        permission = IsSuperUser()
        assert permission.has_permission(request, None) is True

    def test_is_superuser_denied_staff(self, factory, staff_user):
        request = factory.get('/')
        request.user = staff_user
        permission = IsSuperUser()
        assert permission.has_permission(request, None) is False

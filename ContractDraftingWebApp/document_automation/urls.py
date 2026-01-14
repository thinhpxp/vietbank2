from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FieldViewSet, LoanProfileViewSet, DocumentTemplateViewSet, 
    FieldGroupViewSet, UserViewSet, RoleViewSet, FormViewViewSet, 
    MasterObjectViewSet, MasterObjectTypeViewSet,
    MasterObjectRelationViewSet, GroupViewSet, PermissionViewSet,
    AuditLogViewSet, RegistrationView, ProfileView, ChangePasswordView # ADDED
)

router = DefaultRouter()
router.register(r'fields', FieldViewSet)
router.register(r'loan-profiles', LoanProfileViewSet)
router.register(r'document-templates', DocumentTemplateViewSet)
router.register(r'groups', FieldGroupViewSet)
router.register(r'users', UserViewSet)
router.register(r'user-groups', GroupViewSet)
router.register(r'user-permissions', PermissionViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'form-views', FormViewViewSet)
router.register(r'object-types', MasterObjectTypeViewSet)
router.register(r'master-objects', MasterObjectViewSet, basename='master-objects')
router.register(r'master-relations', MasterObjectRelationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegistrationView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='profile-me'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
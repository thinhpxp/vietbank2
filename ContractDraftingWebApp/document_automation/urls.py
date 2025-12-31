from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FieldViewSet, LoanProfileViewSet, PersonViewSet, DocumentTemplateViewSet, FieldGroupViewSet, UserViewSet, RoleViewSet, FormViewViewSet, MasterPersonViewSet, MasterAssetViewSet

router = DefaultRouter()
router.register(r'fields', FieldViewSet)
router.register(r'loan-profiles', LoanProfileViewSet)
router.register(r'people', PersonViewSet)
router.register(r'document-templates', DocumentTemplateViewSet)
router.register(r'groups', FieldGroupViewSet)
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'form-views', FormViewViewSet)
router.register(r'master-people', MasterPersonViewSet, basename='master-people')
router.register(r'master-assets', MasterAssetViewSet, basename='master-assets')

urlpatterns = [
    path('', include(router.urls)),
]
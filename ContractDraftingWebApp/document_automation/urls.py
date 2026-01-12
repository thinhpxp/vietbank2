from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FieldViewSet, LoanProfileViewSet, DocumentTemplateViewSet, 
    FieldGroupViewSet, UserViewSet, RoleViewSet, FormViewViewSet, 
    MasterObjectViewSet, MasterObjectTypeViewSet,
    MasterObjectRelationViewSet # ADDED
)

router = DefaultRouter()
router.register(r'fields', FieldViewSet)
router.register(r'loan-profiles', LoanProfileViewSet)
router.register(r'document-templates', DocumentTemplateViewSet)
router.register(r'groups', FieldGroupViewSet)
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'form-views', FormViewViewSet)
router.register(r'object-types', MasterObjectTypeViewSet)
router.register(r'master-objects', MasterObjectViewSet, basename='master-objects')
router.register(r'master-relations', MasterObjectRelationViewSet) # ADDED

urlpatterns = [
    path('', include(router.urls)),
]
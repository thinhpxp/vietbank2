from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FieldViewSet, LoanProfileViewSet, PersonViewSet, DocumentTemplateViewSet

router = DefaultRouter()
router.register(r'fields', FieldViewSet)
router.register(r'loan-profiles', LoanProfileViewSet)
router.register(r'people', PersonViewSet)
router.register(r'document-templates', DocumentTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
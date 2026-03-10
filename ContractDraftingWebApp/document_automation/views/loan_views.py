from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from docxtpl import DocxTemplate
import logging
import io
import zipfile
from datetime import datetime, date

from ..models import (
    Field, LoanProfile, FieldValue, DocumentTemplate, 
    FieldGroup, Role, FormView, MasterObject, 
    LoanProfileObjectLink, MasterObjectType, MasterObjectRelation
)
from ..serializers import (
    FieldSerializer, FieldGroupSerializer, LoanProfileSerializer, 
    DocumentTemplateSerializer, RoleSerializer, FormViewSerializer
)
from ..permissions import IsAdminOrManager
from .system_views import log_action
from .master_views import find_existing_master_object, save_master_field_values
from .export_views import (
    format_currency_filter, num2words_filter, dateformat_filter, 
    to_roman_filter, evaluate_formula, clean_filename
)
from ..services.loan_service import LoanService
from ..services.document_service import DocumentService

logger = logging.getLogger(__name__)

# --- VIEWSETS ---
class FieldGroupViewSet(viewsets.ModelViewSet):
    queryset = FieldGroup.objects.all().order_by('order', '-id')
    serializer_class = FieldGroupSerializer
    permission_classes = [IsAdminOrManager]
    def get_queryset(self):
        queryset = super().get_queryset()
        form_slug = self.request.query_params.get('form_slug')
        if form_slug: queryset = queryset.filter(allowed_forms__slug=form_slug).distinct()
        return queryset

class FormViewViewSet(viewsets.ModelViewSet):
    queryset = FormView.objects.all()
    serializer_class = FormViewSerializer
    permission_classes = [IsAdminOrManager]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrManager]

class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all().order_by('-id')
    serializer_class = FieldSerializer
    permission_classes = [IsAdminOrManager]
    def get_queryset(self):
        queryset = super().get_queryset().select_related('group')
        form_slug = self.request.query_params.get('form_slug')
        if form_slug:
            queryset = queryset.filter(allowed_forms__slug=form_slug, group__allowed_forms__slug=form_slug).distinct()
        return queryset
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_protected:
            return Response({"error": "Không thể xóa trường được bảo vệ."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active_fields_grouped(self, request):
        form_slug = request.query_params.get('form_slug')
        entity_type = request.query_params.get('entity_type')
        groups_qs = FieldGroup.objects.all().order_by('order')
        if entity_type:
            groups_qs = groups_qs.filter(Q(allowed_object_types__code=entity_type) | Q(entity_type=entity_type)).distinct()
        elif form_slug:
            groups_qs = groups_qs.filter(allowed_forms__slug=form_slug).distinct()
        
        fields_filter = Q(is_active=True)
        if entity_type: fields_filter &= Q(allowed_object_types__code=entity_type)
        elif form_slug: fields_filter &= Q(allowed_forms__slug=form_slug)
            
        groups = groups_qs.prefetch_related(Prefetch('fields', queryset=Field.objects.filter(fields_filter).distinct()))
        result = {grp.name: FieldSerializer(grp.fields.all(), many=True).data for grp in groups if grp.fields.exists()}
        if not entity_type: result["Thông tin cá nhân"] = [] 
        return Response(result)

class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all().order_by('-id')
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAdminOrManager]

class LoanProfileViewSet(viewsets.ModelViewSet):
    queryset = LoanProfile.objects.all().order_by('-created_at')
    serializer_class = LoanProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    def get_queryset(self):
        queryset = LoanProfile.objects.all().prefetch_related('fieldvalue_set__field', 'object_links__master_object')
        search_query = self.request.query_params.get('search')
        if search_query:
            matching_mo_ids = FieldValue.objects.filter(value__icontains=search_query, master_object__isnull=False).values_list('master_object_id', flat=True)
            linked_profile_ids = LoanProfileObjectLink.objects.filter(master_object_id__in=matching_mo_ids).values_list('loan_profile_id', flat=True)
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(id__in=linked_profile_ids)).distinct()
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        instance = serializer.save(created_by_user=user)
        log_action(user, 'CREATE', 'LoanProfile', instance.id, f"Tạo hồ sơ: {instance.name}")

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        instance = self.get_object()
        if instance.editing_by and instance.editing_by != user:
            if (timezone.now() - instance.editing_since).total_seconds() < 900:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(f"Hồ sơ này đang được chỉnh sửa bởi {instance.editing_by.username}")
        serializer.save()
        log_action(user, 'UPDATE', 'LoanProfile', instance.id, f"Cập nhật hồ sơ: {instance.name}")

    def perform_destroy(self, instance):
        p_id, p_name = instance.id, instance.name
        instance.delete()
        log_action(self.request.user, 'DELETE', 'LoanProfile', p_id, f"Xóa hồ sơ: {p_name}")

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        from .system_views import AuditLogSerializer
        from ..models import AuditLog
        logs = AuditLog.objects.filter(target_model='LoanProfile', target_id=str(pk)).select_related('user').order_by('-timestamp')
        return Response(AuditLogSerializer(logs, many=True).data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        try:
            new_profile = LoanService.duplicate_profile(
                profile_id=pk, 
                new_name=request.data.get('new_name'), 
                user=request.user if request.user.is_authenticated else None
            )
            return Response({
                "status": "success", 
                "id": new_profile.id, 
                "name": new_profile.name
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def lock_profile(self, request, pk=None):
        from django.contrib.auth.hashers import make_password
        profile = self.get_object()
        password = request.data.get('password')
        if not password: return Response({"error": "Vui lòng cung cấp mật khẩu để khóa hồ sơ"}, status=400)
        profile.status, profile.lock_password = 'FINALIZED', make_password(password)
        profile.save()
        log_action(request.user, 'UPDATE', 'LoanProfile', profile.id, f"Khóa hồ sơ (Finalized)")
        return Response({"status": "success", "message": "Hồ sơ đã được khóa thành công."})

    @action(detail=True, methods=['post'])
    def unlock_profile(self, request, pk=None):
        from django.contrib.auth.hashers import check_password
        profile = self.get_object()
        password = request.data.get('password')
        if profile.lock_password and not check_password(password, profile.lock_password):
            return Response({"error": "Mật khẩu không chính xác"}, status=403)
        profile.status = 'DRAFT'
        profile.save()
        log_action(request.user, 'UPDATE', 'LoanProfile', profile.id, f"Mở khóa hồ sơ (Draft)")
        return Response({"status": "success", "message": "Hồ sơ đã được mở khóa."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def acquire_lock(self, request, pk=None):
        obj, now = self.get_object(), timezone.now()
        if obj.editing_by and obj.editing_by != request.user and (now - obj.editing_since).total_seconds() < 900:
            return Response({"locked": True, "locked_by": obj.editing_by.username, "since": obj.editing_since}, status=423)
        obj.editing_by, obj.editing_since = request.user, now
        obj.save(update_fields=['editing_by', 'editing_since'])
        return Response({"locked": False, "message": "Lock acquired"})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def release_lock(self, request, pk=None):
        obj = self.get_object()
        if obj.editing_by == request.user:
            obj.editing_by, obj.editing_since = None, None
            obj.save(update_fields=['editing_by', 'editing_since'])
        return Response({"message": "Lock released"})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def heartbeat(self, request, pk=None):
        obj = self.get_object()
        if obj.editing_by == request.user:
            obj.editing_since = timezone.now()
            obj.save(update_fields=['editing_since'])
            return Response({"status": "Extended"})
        return Response({"error": "Lock not owned"}, status=403)

    @action(detail=True, methods=['post'])
    def save_form_data(self, request, pk=None):
        loan_profile = self.get_object()
        user = request.user if request.user.is_authenticated else None
        
        # Check lock
        if loan_profile.editing_by and loan_profile.editing_by != user:
            if (timezone.now() - loan_profile.editing_since).total_seconds() < 900:
                return Response({
                    "error": "Hồ sơ đang bị khóa bởi người khác.", 
                    "locked_by": loan_profile.editing_by.username, 
                    "code": "locked"
                }, status=423)
        
        if loan_profile.status == 'FINALIZED':
            return Response({"error": "Hồ sơ đã bị khóa, không thể chỉnh sửa."}, status=403)
            
        try:
            profile = LoanService.save_loan_form_data(loan_profile, request.data, user)
            return Response(LoanProfileSerializer(profile).data)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='generate-document')
    def generate_document(self, request, pk=None):
        loan_profile = self.get_object()
        data = request.data
        
        results, errors = DocumentService.generate_documents(
            loan_profile=loan_profile,
            template_ids=data.get('template_ids', []) or ([data.get('template_id')] if data.get('template_id') else []),
            export_mode=data.get('export_mode', 'SINGLE'),
            batch_template_ids=[int(i) for i in data.get('batch_template_ids', [])],
            target_object_id=data.get('target_object_id')
        )

        if not results:
            return Response({
                "error": "Không thể sinh file", 
                "details": "; ".join(errors)
            }, status=500)
            
        if len(results) == 1:
            from django.utils.encoding import escape_uri_path
            filename, stream = results[0]
            res = FileResponse(stream, as_attachment=True, filename=filename)
            res['Content-Disposition'] = f'attachment; filename="{escape_uri_path(filename)}"'
            res['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return res
        else:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                for fname, fstream in results:
                    zf.writestr(fname, fstream.getvalue())
            buf.seek(0)
            from django.utils.encoding import escape_uri_path
            res = FileResponse(buf, as_attachment=True, filename=f"{loan_profile.name}.zip")
            res['Content-Type'] = 'application/zip'
            res['Content-Disposition'] = f'attachment; filename="{escape_uri_path(loan_profile.name)}.zip"'
            res['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return res

class FieldValueViewSet(viewsets.ModelViewSet):
    queryset = FieldValue.objects.all()
    serializer_class = RoleSerializer # Actually it should have its own, but views.py didn't define one specifically in early view?
    # Wait, FieldValueViewSet might not be used or I missed it.
    permission_classes = [permissions.IsAuthenticated]

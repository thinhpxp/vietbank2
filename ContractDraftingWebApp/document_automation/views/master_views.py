from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
import logging

from ..models import MasterObjectType, MasterObject, MasterObjectRelation, Field, FieldValue
from ..serializers import MasterObjectTypeSerializer, MasterObjectSerializer, MasterObjectRelationSerializer
from ..permissions import IsAdminOrManager
from .system_views import log_action, format_changes

logger = logging.getLogger(__name__)

# --- HELPERS ---
def save_master_field_values(instance, field_values):
    """Generic helper để lưu dynamic field values cho MasterObject"""
    if not field_values: return
    for key, val in field_values.items():
        try:
            field_obj = Field.objects.get(placeholder_key=key)
            FieldValue.objects.update_or_create(
                master_object=instance,
                loan_profile=None,
                field=field_obj,
                defaults={'value': str(val)}
            )
        except Field.DoesNotExist:
            continue

def find_existing_master_object(object_type, field_values):
    """Tìm kiếm MasterObject đã tồn tại dựa trên identity_field_key của loại đối tượng đó"""
    if not object_type or not field_values: return None
    try:
        obj_type_config = MasterObjectType.objects.filter(code=object_type).first()
        if not obj_type_config or not obj_type_config.identity_field_key: return None
        id_key = obj_type_config.identity_field_key
        id_value = str(field_values.get(id_key, '')).strip()
        forbidden_identifiers = ['n/a', 'none', 'không có', 'khong co', 'chưa có', 'chua co', '_____']
        if not id_value or len(id_value) < 3 or any(f in id_value.lower() for f in forbidden_identifiers): return None
        matching_fv = FieldValue.objects.filter(
            master_object__object_type=object_type,
            master_object__deleted_at__isnull=True,
            field__placeholder_key=id_key,
            value=id_value,
            loan_profile__isnull=True
        ).first()
        return matching_fv.master_object if matching_fv else None
    except Exception as e:
        logger.error(f"Error in find_existing_master_object: {e}")
        return None

def get_identity_value(instance):
    """Lấy giá trị định danh hiện tại của MasterObject từ FieldValue"""
    if not instance or not instance.object_type: return None
    obj_type_cfg = MasterObjectType.objects.filter(code=instance.object_type).first()
    if not obj_type_cfg or not obj_type_cfg.identity_field_key: return None
    
    id_fv = FieldValue.objects.filter(
        master_object=instance,
        field__placeholder_key=obj_type_cfg.identity_field_key,
        loan_profile__isnull=True
    ).first()
    return str(id_fv.value).strip() if id_fv else None

# --- VIEWSETS ---
class MasterObjectTypeViewSet(viewsets.ModelViewSet):
    queryset = MasterObjectType.objects.all().order_by('-id')
    serializer_class = MasterObjectTypeSerializer
    permission_classes = [IsAdminOrManager]
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system:
            return Response({"error": "Không thể xóa loại đối tượng hệ thống mặc định."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class MasterObjectViewSet(viewsets.ModelViewSet):
    serializer_class = MasterObjectSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    def get_queryset(self):
        qs = MasterObject.objects.filter(deleted_at__isnull=True).order_by('-id')
        include_drafts = self.request.query_params.get('include_drafts', 'false').lower() == 'true'
        if getattr(self, 'detail', False): return MasterObject.objects.all()
        if not include_drafts: qs = qs.filter(is_draft=False)
        object_types = self.request.query_params.get('object_type', None)
        if object_types:
            codes = [c.strip() for c in object_types.split(',') if c.strip()]
            if codes: qs = qs.filter(object_type__in=codes)
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrManager])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids: return Response({"error": "Danh sách ID không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                deleted_count = MasterObject.objects.filter(id__in=ids, deleted_at__isnull=True).update(deleted_at=timezone.now())
                log_action(request.user, 'DELETE', 'MasterObject:BULK', 0, f"Xóa hàng loạt {deleted_count} đối tượng: {ids}")
                return Response({"status": "success", "message": f"Đã xóa {deleted_count} đối tượng thành công."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def acquire_lock(self, request, pk=None):
        obj = self.get_object()
        now = timezone.now()
        if obj.editing_by and obj.editing_by != request.user:
            if (now - obj.editing_since).total_seconds() < 900:
                logger.info(f"Lock denied for {request.user.username} on obj {pk}. Already held by {obj.editing_by.username}")
                return Response({"locked": True, "locked_by": obj.editing_by.username, "since": obj.editing_since}, status=423)
        obj.editing_by = request.user
        obj.editing_since = now
        obj.save(update_fields=['editing_by', 'editing_since'])
        logger.info(f"Lock acquired by {request.user.username} on obj {pk}")
        return Response({"locked": False, "message": "Lock acquired"})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def release_lock(self, request, pk=None):
        obj = self.get_object()
        if obj.editing_by == request.user:
            obj.editing_by = None
            obj.editing_since = None
            obj.save(update_fields=['editing_by', 'editing_since'])
            logger.info(f"Lock released by {request.user.username} on obj {pk}")
        return Response({"message": "Lock released"})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def heartbeat(self, request, pk=None):
        obj = self.get_object()
        if obj.editing_by == request.user:
            obj.editing_since = timezone.now()
            obj.save(update_fields=['editing_since'])
            return Response({"status": "Extended"})
        return Response({"error": "Lock not owned"}, status=403)

    def perform_create(self, serializer):
        object_type = self.request.data.get('object_type')
        field_values = self.request.data.get('field_values', {})
        existing = find_existing_master_object(object_type, field_values)
        if existing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"message": f"Dữ liệu này đã tồn tại trong hệ thống (ID: {existing.id})", "code": "duplicate"})
        user = self.request.user if self.request.user.is_authenticated else None
        instance = serializer.save(last_updated_by=user)
        save_master_field_values(instance, field_values)
        log_action(user, 'CREATE', f'MasterObject:{object_type}', instance.id, f"Tạo mới dữ liệu gốc")

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        instance = self.get_object()
        if instance.editing_by and instance.editing_by != user:
            if (timezone.now() - instance.editing_since).total_seconds() < 900:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(f"Đối tượng này đang bị khóa bởi {instance.editing_by.username}")
        old_fvs = {fv.field.placeholder_key: fv.value for fv in FieldValue.objects.filter(master_object=instance, loan_profile__isnull=True)}
        instance = serializer.save(last_updated_by=user)
        field_values = self.request.data.get('field_values', {})
        save_master_field_values(instance, field_values)
        
        # 4. LOG DIFF
        changed = {}
        all_keys = set(old_fvs.keys()) | set(field_values.keys())
        for k in all_keys:
            old_v = old_fvs.get(k, '')
            new_v = field_values.get(k, '')
            if str(old_v) != str(new_v):
                changed[k] = {"from": old_v, "to": new_v}
        
        if changed:
            formatted_detail = f"Cập nhật thông tin: {format_changes(changed)}"
            log_action(user, 'UPDATE', f'MasterObject:{instance.object_type}', instance.id, formatted_detail)
        else:
            log_action(user, 'UPDATE', f'MasterObject:{instance.object_type}', instance.id, "Cập nhật MasterObject")

    def perform_destroy(self, instance):
        o_id, o_type = instance.id, instance.object_type
        instance.deleted_at = timezone.now()
        instance.save()
        log_action(self.request.user, 'DELETE', f'MasterObject:{o_type}', o_id, f"Xóa hờ dữ liệu gốc")

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Tìm kiếm đối tượng toàn hệ thống (dữ liệu gốc)"""
        query = request.query_params.get('q', '').strip()
        obj_type = request.query_params.get('object_type')
        
        if not query or len(query) < 2:
            return Response([])

        # Tìm trong FieldValue của MasterObject (loan_profile__isnull=True)
        matching_master_ids = FieldValue.objects.filter(
            master_object__isnull=False,
            loan_profile__isnull=True,
            value__icontains=query
        ).values_list('master_object_id', flat=True).distinct()
        
        qs = MasterObject.objects.filter(id__in=matching_master_ids, deleted_at__isnull=True)
        if obj_type:
            qs = qs.filter(object_type=obj_type)
            
        # Giới hạn 20 kết quả để tối ưu hiệu năng
        qs = qs[:20]
        
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def check_identity(self, request):
        obj_type, key, value = request.query_params.get('object_type'), request.query_params.get('key'), request.query_params.get('value')
        if not all([obj_type, key, value]): return Response({"error": "Missing params"}, status=400)
        existing = find_existing_master_object(obj_type, {key: value})
        if existing: return Response({"exists": True, "id": existing.id, "display_name": existing.display_name})
        return Response({"exists": False})

    @action(detail=True, methods=['get'])
    def related_profiles(self, request, pk=None):
        master_obj = self.get_object()
        from ..models import LoanProfileObjectLink
        links = LoanProfileObjectLink.objects.filter(master_object=master_obj).select_related('loan_profile')
        data = [{'id': link.loan_profile.id, 'name': link.loan_profile.name, 'created_at': link.loan_profile.created_at, 'form_name': link.loan_profile.form_view.name if link.loan_profile.form_view else 'Mặc định'} for link in links]
        return Response(data)

class MasterObjectRelationViewSet(viewsets.ModelViewSet):
    queryset = MasterObjectRelation.objects.all().order_by('-created_at')
    serializer_class = MasterObjectRelationSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    @action(detail=False, methods=['post'])
    def create_relation(self, request):
        source_id, target_id, rtype = request.data.get('source_id'), request.data.get('target_id'), request.data.get('relation_type', 'OWNER')
        if not source_id or not target_id: return Response({"error": "Thiếu source_id hoặc target_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            source, target = MasterObject.objects.get(id=source_id), MasterObject.objects.get(id=target_id)
            relation, created = MasterObjectRelation.objects.get_or_create(source_object=source, target_object=target, relation_type=rtype)
            return Response(MasterObjectRelationSerializer(relation).data)
        except MasterObject.DoesNotExist: return Response({"error": "Không tìm thấy đối tượng"}, status=status.HTTP_404_NOT_FOUND)

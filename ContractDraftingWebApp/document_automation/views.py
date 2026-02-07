from rest_framework import viewsets, status, permissions
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User, Group, Permission
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .permissions import IsAdminOrManager # IMPORT CUSTOM PERMISSION
from rest_framework.views import APIView

# ... (rest of imports)

# ... (omitted code)


from django.db.models import Q, Prefetch
from django.utils import timezone
from django.db import transaction
# --- CÁC IMPORT MỚI CHO CHỨC NĂNG XUẤT WORD ---
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from docxtpl import DocxTemplate
from datetime import datetime, date
import os
import io
import zipfile
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from num2words import num2words # Cần pip install num2words
import decimal
from jinja2 import Environment
# Import Models
from .models import (
    Field, LoanProfile, FieldValue, 
    DocumentTemplate, FieldGroup, Role, 
    FormView, MasterObject, LoanProfileObjectLink,
    MasterObjectType, MasterObjectRelation, AuditLog # ADDED
)

# Import Serializers
from .serializers import (
    FieldSerializer, FieldGroupSerializer, LoanProfileSerializer, 
    FieldValueSerializer, DocumentTemplateSerializer,
    RoleSerializer, GroupSerializer, PermissionSerializer,
    UserSerializer, RegistrationSerializer, PasswordChangeSerializer, 
    FormViewSerializer, MasterObjectSerializer, 
    LoanProfileObjectLinkSerializer, MasterObjectTypeSerializer,
    MasterObjectRelationSerializer, AuditLogSerializer # ADDED
)
# --- CÁC HÀM HỖ TRỢ JINJA2 (FORMAT TIỀN, NGÀY, CHỮ) ---
def format_currency_filter(value):
    """Chuyển số thành dạng tiền tệ (VD: 1.000.000)"""
    if not value: return ""
    try:
        d_value = decimal.Decimal(str(value))
        return "{:,.0f}".format(d_value).replace(",", ".")
    except:
        return str(value)

def num2words_filter(value):
    """Chuyển số thành chữ Tiếng Việt (có hỗ trợ số thập phân)"""
    if not value: return ""
    try:
        import re
        # Chuẩn hóa: phẩy -> chấm, xóa khoảng trắng
        s_val = str(value).replace(',', '.').replace(' ', '')
        # Loại bỏ các dấu chấm phân tách hàng nghìn (dots that are not the decimal point)
        # Tuy nhiên, cách an toàn nhất là chỉ giữ lại dấu chấm cuối cùng nếu có nhiều hơn 1 dot
        # Hoặc đơn giản hơn: Theo logic mới của Frontend, state chỉ có duy nhất 1 dấu chấm cho decimal.
        # Vậy ta chỉ cần strip mọi dấu chấm trừ cái cuối cùng? Không, strip mọi dấu chấm trừ cái duy nhất.
        
        # Logic: Tìm dot cuối cùng. Xóa tất cả dot khác.
        parts = s_val.split('.')
        if len(parts) > 2:
            # Có nhiều hơn 1 dot -> Có dấu phân tách nghìn lọt vào
            clean_val = "".join(parts[:-1]) + "." + parts[-1]
        else:
            clean_val = s_val
            
        # Chỉ giữ lại số và dấu chấm
        clean_val = re.sub(r'[^\d.]', '', clean_val)
        
        if not clean_val: return str(value)
        
        # Đọc số (Dùng float nếu có dấu chấm)
        if '.' in clean_val:
            val_to_read = float(clean_val)
        else:
            val_to_read = int(clean_val)
            
        result = num2words(val_to_read, lang='vi').capitalize()
        return result
    except Exception as e:
        print(f"DEBUG: num2words_filter failed for value '{value}': {e}")
        return str(value)

def to_roman_filter(value):
    """Chuyển số thành ký tự La Mã viết thường (i, ii, iii...)"""
    try:
        n = int(value)
        if not 0 < n < 4000: return str(value)
        millions = ["", "m", "mm", "mmm"]
        hundreds = ["", "c", "cd", "d", "dc", "dcc", "dccc", "cm"]
        tens = ["", "x", "xx", "xxx", "xl", "l", "lx", "lxx", "lxxx", "xc"]
        ones = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"]
        return millions[n // 1000] + hundreds[(n % 1000) // 100] + tens[(n % 100) // 10] + ones[n % 10]
    except:
        return str(value)

def dateformat_filter(value, fmt="%d/%m/%Y"):
    """
    Định dạng ngày tháng thông minh. 
    Hỗ trợ cả object datetime và chuỗi văn bản (kể cả chuỗi thiếu thông tin).
    Nếu thành phần nào thiếu (ví dụ ngày trống), sẽ tự động điền dấu chấm vào vị trí đó.
    """
    import re
    empty_dots = " . . . . "
    
    if not value: 
        return " . . . . . . . . " if fmt == "%d/%m/%Y" else empty_dots
        
    # 1. Thử parse thành object datetime nếu là chuỗi chuẩn
    dt = None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        for str_fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
            try:
                dt = datetime.strptime(value.strip(), str_fmt)
                break
            except:
                continue
                
    if dt:
        return dt.strftime(fmt)
        
    # 2. Xử lý chuỗi "văn bản tự do" (ví dụ: " /12/2025")
    if isinstance(value, str):
        # Tách chuỗi bằng các ký tự phân cách phổ biến
        parts = re.split(r'[/.\-]', value.strip())
        
        # Dự đoán vị trí Ngày, Tháng, Năm
        day = month = year = None
        
        if len(parts) == 3:
            # Giả định định dạng DD/MM/YYYY hoặc YYYY-MM-DD
            if len(parts[0]) == 4: # YYYY-MM-DD
                year, month, day = parts
            else: # DD/MM/YYYY
                day, month, year = parts
        elif len(parts) == 2: # MM/YYYY
            month, year = parts
            
        # Hàm kiểm tra xem một phần có "hợp lệ" hay không
        def clean_part(v):
            if not v or not re.search(r'\d', str(v)):
                return empty_dots
            return str(v).strip()
            
        # Thay thế các token trong định dạng bằng giá trị tương ứng
        res = fmt
        res = res.replace('%d', clean_part(day))
        res = res.replace('%m', clean_part(month))
        res = res.replace('%Y', clean_part(year))
        # Hỗ trợ năm rút gọn %y
        y_val = clean_part(year)
        res = res.replace('%y', y_val[-2:] if len(y_val) >= 2 and y_val != empty_dots else empty_dots)
        
        return res
        
    return str(value) if value else " . . . . . . . . "
# --- HELPER GHI LOG ---
def log_action(user, action, target_model, target_id=None, details=None):
    """Ghi nhật ký thao tác người dùng"""
    try:
        if user and user.is_authenticated:
            AuditLog.objects.create(
                user=user,
                action=action,
                target_model=target_model,
                target_id=str(target_id) if target_id else None,
                details=details
            )
    except Exception as e:
        print(f"Lỗi ghi AuditLog: {e}")

# --- SIGNALS CHO LOGIN/LOGOUT ---
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_action(user, 'LOGIN', 'User', user.id, f"Người dùng {user.username} đăng nhập")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_action(user, 'LOGOUT', 'User', user.id, f"Người dùng {user.username} đăng xuất")
# 1.1 ViewSet cho FieldGroup
class FieldGroupViewSet(viewsets.ModelViewSet):
    queryset = FieldGroup.objects.all().order_by('order')
    serializer_class = FieldGroupSerializer
    permission_classes = [IsAdminOrManager]

    def get_queryset(self):
        queryset = super().get_queryset()
        form_slug = self.request.query_params.get('form_slug')
        if form_slug is not None:
            # Chết độ lọc nghiêm ngặt: Chỉ lấy những nhóm được gắn trực tiếp với form này
            queryset = queryset.filter(allowed_forms__slug=form_slug).distinct()
        return queryset

# 1.1b ViewSet cho FormView
class FormViewViewSet(viewsets.ModelViewSet):
    queryset = FormView.objects.all()
    serializer_class = FormViewSerializer
    permission_classes = [IsAdminOrManager]

# 1.3 ViewSet cho Role
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrManager]

# 1.2 ViewSet cho Field
class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [IsAdminOrManager]

    def get_queryset(self):
        queryset = super().get_queryset().select_related('group')
        form_slug = self.request.query_params.get('form_slug')
        if form_slug is not None:
            # Chết độ cực kỳ nghiêm ngặt: Phải được gán đích danh Form này 
            # VÀ Nhóm của nó cũng phải được gán cho Form này
            queryset = queryset.filter(
                allowed_forms__slug=form_slug,
                group__allowed_forms__slug=form_slug
            ).distinct()
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Ngăn xóa các trường được bảo vệ"""
        instance = self.get_object()
        if instance.is_protected:
            return Response(
                {"error": "Không thể xóa trường được bảo vệ."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)



    @action(detail=False, methods=['get'])
    def active_fields_grouped(self, request):
        """Trả về danh sách trường active nhóm theo FieldGroup, có lọc theo form_slug hoặc entity_type"""
        form_slug = request.query_params.get('form_slug')
        entity_type = request.query_params.get('entity_type') # MỚI: Lọc theo đối tượng (PERSON, ASSET, ...)
        
        from django.db.models import Q
        
        # 1. Lọc nhóm
        groups_qs = FieldGroup.objects.all().order_by('order')
        if entity_type:
            # Sử dụng allowed_object_types (M2M) thay vì object_type (FK)
            # Cho phép 1 group liên kết với nhiều object types
            groups_qs = groups_qs.filter(
                Q(allowed_object_types__code=entity_type) | 
                Q(entity_type=entity_type)
            ).distinct()
        elif form_slug:
            groups_qs = groups_qs.filter(allowed_forms__slug=form_slug).distinct()
            
        # 2. Prefetch fields
        fields_filter = Q(is_active=True)
        
        # NEW: If entity_type is provided, filter fields by allowed_object_types containing this type
        if entity_type:
            fields_filter &= Q(allowed_object_types__code=entity_type)
        elif form_slug:
            # Nếu là Hồ sơ (có form_slug), ta lọc fields được phép hiển thị ở form đó
            fields_filter &= Q(allowed_forms__slug=form_slug)
            
        groups = groups_qs.prefetch_related(
            Prefetch('fields', queryset=Field.objects.filter(fields_filter).distinct())
        )

        result = {}
        for grp in groups:
            fields_data = FieldSerializer(grp.fields.all(), many=True).data
            if fields_data:
                result[grp.name] = fields_data

        # Synthetic fields: Chỉ hiện ở bản cũ hoặc khi không có entity_type
        if not entity_type:
            result["Thông tin cá nhân"] = [] 

        return Response(result)

# PersonViewSet removed


# 3.1 ViewSet cho DocumentTemplate
class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAdminOrManager]

# 3.2 ViewSet cho User (Nâng cấp)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile').prefetch_related('groups').order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        """Action dành riêng cho Admin để đặt lại mật khẩu cho User"""
        user = self.get_object()
        new_password = request.data.get('password')
        
        if not new_password:
            return Response({"error": "Vui lòng cung cấp mật khẩu mới."}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.save()
        
        log_action(request.user, 'UPDATE', 'User', user.id, f"Admin đã đặt lại mật khẩu cho {user.username}")
        return Response({"status": "success", "message": f"Đã đặt lại mật khẩu cho user {user.username}"})

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().prefetch_related('permissions').order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrManager]

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    # Lọc bỏ các quyền kỹ thuật/hệ thống không cần thiết cho Admin nghiệp vụ
    queryset = Permission.objects.exclude(
        content_type__app_label__in=['sessions', 'contenttypes', 'admin']
    ).select_related('content_type').order_by('content_type__model', 'codename')
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminOrManager]
    pagination_class = None # Đảm bảo không bị phân trang làm mất quyền

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(codename__icontains=search) | 
                Q(content_type__app_label__icontains=search) |
                Q(content_type__model__icontains=search)
            )
        return queryset

# --- NEW AUTH VIEWS ---
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            log_action(user, 'CREATE', 'User', user.id, f"Đăng ký tài khoản mới: {user.username}")
            return Response({"status": "success", "message": "Đăng ký thành công!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"status": "success", "message": "Đổi mật khẩu thành công!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import django_filters

class AuditLogFilter(django_filters.FilterSet):
    timestamp_gte = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='gte')
    timestamp_lte = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='lte')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')

    class Meta:
        model = AuditLog
        fields = ['action', 'username', 'target_model', 'timestamp_gte', 'timestamp_lte']

class AuditLogPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    pagination_class = AuditLogPagination
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = ['details', 'target_id', 'target_model']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']

    # Removed custom get_queryset as filter_backends handles it better

# 4. ViewSet cho LoanProfile (Logic chính)
class LoanProfileViewSet(viewsets.ModelViewSet):
    queryset = LoanProfile.objects.all().order_by('-created_at')
    serializer_class = LoanProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            # Tìm kiếm theo tên hồ sơ HOẶC theo giá trị của các MasterObject liên kết
            # (VD: Tìm theo số hiệu HĐTC nằm trong MasterObject)
            
            # 1. Tìm IDs của MasterObjects có giá trị khớp search_query
            matching_mo_ids = FieldValue.objects.filter(
                value__icontains=search_query,
                master_object__isnull=False
            ).values_list('master_object_id', flat=True)
            
            # 2. Tìm IDs của LoanProfiles có liên kết với các MasterObjects này
            linked_profile_ids = LoanProfileObjectLink.objects.filter(
                master_object_id__in=matching_mo_ids
            ).values_list('loan_profile_id', flat=True)
            
            # 3. Kết hợp tìm kiếm theo tên hồ sơ và danh sách profile IDs vừa tìm được
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(id__in=linked_profile_ids)
            ).distinct()
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        instance = serializer.save(created_by_user=user)
        log_action(user, 'CREATE', 'LoanProfile', instance.id, f"Tạo hồ sơ: {instance.name}")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'UPDATE', 'LoanProfile', instance.id, f"Cập nhật hồ sơ: {instance.name}")

    def perform_destroy(self, instance):
        p_id = instance.id
        p_name = instance.name
        instance.delete()
        log_action(self.request.user, 'DELETE', 'LoanProfile', p_id, f"Xóa hồ sơ: {p_name}")

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Lấy lịch sử tác động (Audit Log) của hồ sơ này.
        """
        try:
            # Lấy tất cả log có target_model='LoanProfile' và target_id=pk
            logs = AuditLog.objects.filter(
                target_model='LoanProfile',
                target_id=str(pk)
            ).select_related('user').order_by('-timestamp')
            
            serializer = AuditLogSerializer(logs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        API tạo bản sao hồ sơ vay.
        Input: { "new_name": "Tên hồ sơ mới" }
        Output: { "id": new_profile_id, "name": "..." }
        """
        original = self.get_object()
        new_name = request.data.get('new_name', f"Bản sao - {original.name}")
        
        try:
            with transaction.atomic():
                # 1. Tạo hồ sơ mới
                new_profile = LoanProfile.objects.create(
                    name=new_name,
                    form_view=original.form_view,
                    created_by_user=request.user if request.user.is_authenticated else None
                )

                # 2. Sao chép FieldValues chung (không liên kết Object)
                general_fvs = original.fieldvalue_set.filter(master_object__isnull=True)
                for fv in general_fvs:
                    FieldValue.objects.create(
                        loan_profile=new_profile,
                        field=fv.field,
                        value=fv.value
                    )

                # 3. Sao chép Objects (People/Assets/etc)
                for link in original.object_links.all():
                    master_obj = link.master_object
                    # Duplicate link
                    LoanProfileObjectLink.objects.create(
                        loan_profile=new_profile,
                        master_object=master_obj,
                        roles=link.roles
                    )
                    
                    # Duplicate specific FieldValues
                    specific_fvs = original.fieldvalue_set.filter(master_object=master_obj)
                    for fv in specific_fvs:
                        FieldValue.objects.create(
                            loan_profile=new_profile,
                            master_object=master_obj,
                            field=fv.field,
                            value=fv.value
                        )

            return Response({
                "status": "success",
                "id": new_profile.id,
                "name": new_profile.name,
                "message": "Tạo bản sao thành công!"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def lock_profile(self, request, pk=None):
        """Khóa hồ sơ và thiết lập mật khẩu"""
        profile = self.get_object()
        password = request.data.get('password')
        if not password:
            return Response({"error": "Vui lòng cung cấp mật khẩu để khóa hồ sơ"}, status=400)
        
        profile.status = 'FINALIZED'
        profile.lock_password = password
        profile.save()
        log_action(request.user, 'UPDATE', 'LoanProfile', profile.id, f"Khóa hồ sơ (Finalized)")
        return Response({"status": "success", "message": "Hồ sơ đã được khóa thành công."})

    @action(detail=True, methods=['post'])
    def unlock_profile(self, request, pk=None):
        """Mở khóa hồ sơ bằng mật khẩu"""
        profile = self.get_object()
        password = request.data.get('password')
        
        if profile.lock_password and profile.lock_password != password:
            return Response({"error": "Mật khẩu không chính xác"}, status=403)
        
        profile.status = 'DRAFT'
        profile.save()
        log_action(request.user, 'UPDATE', 'LoanProfile', profile.id, f"Mở khóa hồ sơ (Draft)")
        return Response({"status": "success", "message": "Hồ sơ đã được mở khóa."})

    @action(detail=True, methods=['post'])
    def save_form_data(self, request, pk=None):
        """
        API lưu dữ liệu tổng hợp (Generic for Universal Entity)
        """
        loan_profile = self.get_object()
        
        if loan_profile.status == 'FINALIZED':
            return Response({"error": "Hồ sơ đã bị khóa, không thể chỉnh sửa."}, status=403)

        data = request.data
        updating_user = request.user if request.user.is_authenticated else None

        try:
            with transaction.atomic():
                # A. Cập nhật thông tin cơ bản
                if 'name' in data:
                    loan_profile.name = data['name']
                
                form_slug = data.get('form_slug')
                if form_slug:
                    form_v = FormView.objects.filter(slug=form_slug).first()
                    if form_v:
                        loan_profile.form_view = form_v
                
                loan_profile.save()

                # B. Lưu FieldValues chung
                general_fields = data.get('field_values', {})
                for key, val in general_fields.items():
                    try:
                        field_obj = Field.objects.get(placeholder_key=key)
                        FieldValue.objects.update_or_create(
                            loan_profile=loan_profile,
                            master_object=None,
                            field=field_obj,
                            defaults={'value': str(val) if val is not None else ""}
                        )
                    except Field.DoesNotExist:
                        continue

                # C. Xử lý Objects (Unified Logic for People and Assets)
                processed_master_ids = []

                def process_objects(data_list, default_obj_type):
                    for item_data in data_list:
                        obj_id = item_data.get('id')
                        roles = item_data.get('roles', [])
                        fields_dict = item_data.get('individual_field_values') or item_data.get('asset_field_values', {})
                        
                        # Extract actual type from payload if present (NEW)
                        actual_type = default_obj_type
                        if 'master_object' in item_data and item_data['master_object']:
                            actual_type = item_data['master_object'].get('object_type', default_obj_type)
                        
                        # 1. Find or Create MasterObject
                        master_obj = None
                        
                        # SKIP LOGIC: Nếu không có ID (mới) và (không có mã loại hoặc không có dữ liệu fields) -> Bỏ qua
                        is_empty = not any(str(v).strip() for v in fields_dict.values() if v)
                        if not obj_id and (not actual_type or is_empty):
                            print(f"  DEBUG: Skipping empty new object {actual_type}")
                            continue

                        if obj_id:
                            master_obj = MasterObject.objects.filter(id=obj_id).first()
                            if master_obj:
                                master_obj.last_updated_by = updating_user
                                master_obj.save()
                        
                        # DEDUPLICATION LOGIC: Nếu chưa có id, thử tìm theo mã định danh (CCCD, Biển số...)
                        if not master_obj:
                            master_obj = find_existing_master_object(actual_type, fields_dict)
                        
                        if not master_obj:
                            master_obj = MasterObject.objects.create(
                                object_type=actual_type,
                                last_updated_by=updating_user
                            )

                        processed_master_ids.append(master_obj.id)
                        print(f"  DEBUG: Item {actual_type} -> Master:{master_obj.id} Ident:{fields_dict.get('chung_nhan_qsdd', 'N/A')}")

                        # 2. Update Link
                        LoanProfileObjectLink.objects.update_or_create(
                            loan_profile=loan_profile,
                            master_object=master_obj,
                            defaults={'roles': roles}
                        )

                        # 3. Save Specific Field Values
                        for f_key, f_val in fields_dict.items():
                            try:
                                f_obj = Field.objects.get(placeholder_key=f_key)
                                
                                # CHECK: Is this field allowed for this object type?
                                # This prevents leaking fields across types (e.g. real estate fields in vehicle)
                                if f_obj.allowed_object_types.exists():
                                    allowed_codes = f_obj.allowed_object_types.values_list('code', flat=True)
                                    if actual_type not in allowed_codes:
                                        continue # Skip irrelevant field

                                FieldValue.objects.update_or_create(
                                    loan_profile=loan_profile,
                                    master_object=master_obj,
                                    field=f_obj,
                                    defaults={'value': str(f_val)}
                                )

                                # 4. Update Canonical Master Data (loan_profile=None)
                                # This ensures the object appears correctly in Master Data Management
                                FieldValue.objects.update_or_create(
                                    loan_profile=None,
                                    master_object=master_obj,
                                    field=f_obj,
                                    defaults={'value': str(f_val)}
                                )
                            except Field.DoesNotExist:
                                continue

                # New logic: Process object_sections if provided
                object_sections = data.get('object_sections', {})
                print(f"DEBUG: object_sections keys: {list(object_sections.keys())}")
                print(f"DEBUG: Processing {len(object_sections)} sections")
                if object_sections:
                    for t_code, items in object_sections.items():
                        print(f"DEBUG: type {t_code} has {len(items)} items")
                        process_objects(items, t_code)
                else:
                    # Backward compatibility for existing payloads
                    process_objects(data.get('people', []), 'PERSON')
                    process_objects(data.get('attorneys', []), 'ATTORNEY')
                    process_objects(data.get('assets', []), 'ASSET')

                # D. Cleanup
                LoanProfileObjectLink.objects.filter(loan_profile=loan_profile).exclude(
                    master_object__id__in=processed_master_ids
                ).delete()
                
                # E. AUTOMATIC RELATION INFERENCE (Direct Linking)
                # Logic: If a Person has a Role with relation_type (e.g., OWNER), link them to all Assets in this profile.
                # 1. Find potential owners in this profile
                potential_owners = []
                # Re-fetch links to get fresh roles
                profile_links = LoanProfileObjectLink.objects.filter(loan_profile=loan_profile).select_related('master_object')
                
                for link in profile_links:
                    if link.master_object.object_type == 'PERSON':
                        # Check roles
                        if not link.roles: continue
                        
                        # Find if any role implies a relation
                        # We need to query Role table or cache it. Since roles are list of strings (slugs), we match with Role.slug
                        # Optimization: Fetch all system roles with relation_type once
                        system_roles = Role.objects.exclude(relation_type__isnull=True).exclude(relation_type='')
                        
                        for role_str in link.roles:
                            # Match slug OR name (case insensitive safe if needed, but strict for now)
                            matching_role = next((r for r in system_roles if r.slug == role_str or r.name == role_str), None)
                            if matching_role:
                                potential_owners.append({
                                    'person': link.master_object,
                                    'relation': matching_role.relation_type
                                })

                # 2. Find assets in this profile
                assets_in_profile = [link.master_object for link in profile_links if link.master_object.object_type != 'PERSON']
                
                # 3. Create Relations
                if potential_owners and assets_in_profile:
                    for owner_data in potential_owners:
                        person = owner_data['person']
                        rtype = owner_data['relation']
                        
                        for asset in assets_in_profile:
                            # Create or Get Relation
                            MasterObjectRelation.objects.get_or_create(
                                source_object=person,
                                target_object=asset,
                                relation_type=rtype
                            )
                
                FieldValue.objects.filter(loan_profile=loan_profile, master_object__isnull=False).exclude(
                    master_object__id__in=processed_master_ids
                ).delete()

            # Ghi log Audit sau khi commit thành công (chỉ khi không phải auto-save)
            is_auto_save = str(data.get('is_auto_save', 'False')).lower() == 'true'
            if not is_auto_save:
                log_action(
                    updating_user, 
                    'UPDATE', 
                    'LoanProfile', 
                    loan_profile.id, 
                    f"Cập nhật dữ liệu từ Form: {loan_profile.name}"
                )

            serializer = LoanProfileSerializer(loan_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # Tối ưu hóa truy vấn: Lấy luôn dữ liệu bảng con trong 1 lần
        queryset = LoanProfile.objects.all().prefetch_related(
            'fieldvalue_set__field',
            'object_links__master_object'
        )
        return queryset

    @action(detail=True, methods=['post'], url_path='generate-document')
    def generate_document(self, request, pk=None):
        """
        API sinh file Word từ Template và Dữ liệu hồ sơ.
        Input: { "template_id": 1 } hoặc { "template_ids": [1, 2] }
        Output: File .docx hoặc .zip
        """
        loan_profile = self.get_object()
        data = request.data
        
        template_id = data.get('template_id')
        template_ids = data.get('template_ids', [])

        if not template_id and not template_ids:
            return Response({"error": "Vui lòng cung cấp template_id hoặc template_ids."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. CHUẨN BỊ CONTEXT (Dữ liệu để trộn)
        # Refresh from DB to avoid any prefetched/cached data issues
        loan_profile.refresh_from_db()
        context = {}

        # A. Thông tin cơ bản
        context['ten_ho_so'] = loan_profile.name
        
        # Xử lý Ngày lập hồ sơ (ngay_tao) ưu tiên lấy từ trường động 'ngay_lap_ho_so'
        ngay_lap_fv = FieldValue.objects.filter(
            loan_profile=loan_profile,
            field__placeholder_key='ngay_lap_ho_so', 
            master_object__isnull=True
        ).first()
        
        if ngay_lap_fv:
            context['ngay_tao'] = ngay_lap_fv.value if ngay_lap_fv.value else ""
        else:
            context['ngay_tao'] = loan_profile.created_at

        # B. Các trường chung (FieldValues không gắn với MasterObject cụ thể)
        general_fvs = FieldValue.objects.filter(loan_profile=loan_profile, master_object__isnull=True)
        for fv in general_fvs:
            context[fv.field.placeholder_key] = fv.value

        # Helper to fetch relations for Jinja context
        def get_relations_for_object(mo_id):
            relations = {
                'related_assets': [],
                'related_people': [],
                'base_contracts': [],
                'amending_contracts': [],
                'secured_loan_contracts': [], # HĐ tín dụng mà bản thân HĐ này bảo đảm
                'contracts_securing': [],     # HĐ thế chấp bảo đảm cho HĐ tín dụng này
            }
            rels_out = MasterObjectRelation.objects.filter(source_object_id=mo_id).select_related('target_object')
            rels_in = MasterObjectRelation.objects.filter(target_object_id=mo_id).select_related('source_object')
            
            # Helper to get basic data for a related object
            def get_mo_basic_data(mo, rel_type):
                data = {'id': mo.id, 'object_type': mo.object_type, 'relation_type': rel_type}
                # Thêm basic field values từ Master data (loan_profile=null)
                fvs = {fv.field.placeholder_key: fv.value 
                       for fv in FieldValue.objects.filter(master_object=mo, loan_profile__isnull=True)}
                data.update(fvs)
                return data

            for r in rels_out:
                target_data = get_mo_basic_data(r.target_object, r.relation_type)
                relations['related_assets'].append(target_data) 
                if r.relation_type == 'AMENDS': relations['base_contracts'].append(target_data)
                if r.relation_type == 'SECURES': relations['secured_loan_contracts'].append(target_data)

            for r in rels_in:
                source_data = get_mo_basic_data(r.source_object, r.relation_type)
                relations['related_people'].append(source_data)
                if r.relation_type == 'AMENDS': relations['amending_contracts'].append(source_data)
                if r.relation_type == 'SECURES': relations['contracts_securing'].append(source_data)
            
            return relations

        # C. Danh sách People (from Universal)
        people_list = []
        person_links = LoanProfileObjectLink.objects.filter(
            loan_profile=loan_profile, 
            master_object__object_type='PERSON'
        ).select_related('master_object')

        for link in person_links:
            master = link.master_object
            specific_fvs = FieldValue.objects.filter(loan_profile=loan_profile, master_object=master)
            master_fvs = {fv.field.placeholder_key: fv.value 
                          for fv in FieldValue.objects.filter(master_object=master, loan_profile__isnull=True)}
            
            p_data = {
                'id': master.id,
                'roles': link.roles,
            }
            p_data.update(master_fvs)
            for fv in specific_fvs:
                p_data[fv.field.placeholder_key] = fv.value
            
            # Inject relations
            p_data.update(get_relations_for_object(master.id))
            
            if 'ho_ten' not in p_data: p_data['ho_ten'] = master_fvs.get('ho_ten', "")
            if 'cccd_so' not in p_data: p_data['cccd_so'] = master_fvs.get('cccd_so', "")
            people_list.append(p_data)

        context['people'] = people_list

        # D. Danh sách Assets (từ Universal) - GIỜ BAO GỒM CẢ LOẠI CONTRACT
        assets_list = []
        asset_links = LoanProfileObjectLink.objects.filter(
            loan_profile=loan_profile
        ).exclude(
            master_object__object_type='PERSON'
        ).select_related('master_object')

        for link in asset_links:
            master = link.master_object
            specific_fvs = FieldValue.objects.filter(loan_profile=loan_profile, master_object=master)
            master_fvs = {fv.field.placeholder_key: fv.value 
                          for fv in FieldValue.objects.filter(master_object=master, loan_profile__isnull=True)}

            a_data = {
                'id': master.id,
                '_object_type': master.object_type 
            }
            a_data.update(master_fvs)
            for fv in specific_fvs:
                a_data[fv.field.placeholder_key] = fv.value
            
            # Chèn các quan hệ (dẫn chiếu chéo)
            a_data.update(get_relations_for_object(master.id))
                
            assets_list.append(a_data)
        
        context['assets'] = assets_list

        # MỚI: Tự động tạo các Group danh sách theo Object Type (VD: context['REALESTATE'], context['VEHICLE'])
        # Giúp người dùng dùng vòng lặp {% for as in REALESTATE %} trong template
        for a in assets_list:
            obj_type = a.get('_object_type')
            if not obj_type: continue
            
            # 1. Dạng nguyên bản: {% for x in REALESTATE %}
            if obj_type not in context:
                context[obj_type] = []
            context[obj_type].append(a)
            
            # 2. Dạng lowercase_list: {% for x in realestate_list %}
            slug_key = f"{obj_type.lower()}_list"
            if slug_key not in context:
                context[slug_key] = []
            context[slug_key].append(a)

        # F. SIÊU CẢI TIẾN: HỖ TRỢ TRUY XUẤT TRỰC TIẾP (Flattening cho Dedicated Sections)
        # Giúp enduser dùng {{ ten_du_an }} thay vì {{ PROJECT.0.ten_du_an }}
        dedicated_type_codes = list(MasterObjectType.objects.filter(form_display_mode='DEDICATED_SECTION').values_list('code', flat=True))
        
        # Danh sách các key hệ thống không được phép ghi đè
        reserved_keys = ['ten_ho_so', 'ngay_tao', 'people', 'assets', 'tin_dung_list', 'bao_dam_list']
        
        for t_code in dedicated_type_codes:
            items = context.get(t_code, [])
            if items and len(items) > 0:
                # Lấy đối tượng đầu tiên (duy nhất) trong section này
                first_item = items[0]
                for key, val in first_item.items():
                    # Chỉ đưa ra ngoài nếu key không trùng với key hệ thống
                    # ƯU TIÊN: Ghi đè các giá trị chung (thường là defaults) bằng giá trị thực từ Object đã chọn
                    if key not in reserved_keys:
                        context[key] = val

        # E. Tạo các danh sách lọc sẵn dựa trên VAI TRÒ (Gộp cả Slug động và Legacy)
        # 1. Lấy danh sách Role từ DB để làm bản đồ Mapping
        all_system_roles = Role.objects.exclude(slug__isnull=True).exclude(slug='')
        
        # Bản đồ: tên_vai_trò (lowercase) -> slug (lowercase)
        role_name_to_slug = {}
        all_active_slugs = set()
        for r in all_system_roles:
            s = r.slug.strip().lower()
            role_name_to_slug[r.name.strip().lower()] = s
            all_active_slugs.add(s)

        # 2. Định nghĩa các Slug mặc định (Legacy)
        legacy_slug_map = {
            'ben_vay': ['bên vay', 'bên được cấp tín dụng'],
            'ben_duoc_cap_tin_dung': ['bên được cấp tín dụng'],
            'ben_the_chap': ['bên thế chấp', 'bên bảo đảm'],
            'ben_bao_dam': ['bên bảo đảm', 'bên thế chấp', 'bên bảo đảm'],
            'ben_bao_lanh': ['bên bảo lãnh']
        }
        for s in legacy_slug_map:
            all_active_slugs.add(s)

        # 3. Khởi tạo các danh sách trong context (tất cả là lowercase slug)
        role_data_lists = {s: [] for s in all_active_slugs}

        # 4. Phân loại từng người vào các danh sách phù hợp
        for p in people_list:
            p_assigned_roles = [r.strip().lower() for r in p.get('roles', [])]
            matched_slugs = set()
            
            for rname in p_assigned_roles:
                # a. Tìm theo Slug động trong DB
                if rname in role_name_to_slug:
                    matched_slugs.add(role_name_to_slug[rname])
                
                # b. Tìm theo logic Legacy (fallback)
                for l_slug, l_names in legacy_slug_map.items():
                    if rname in l_names:
                        matched_slugs.add(l_slug)
            
            # Đưa người này vào tất cả các danh sách đã khớp
            for s in matched_slugs:
                role_data_lists[s].append(p)
        
        # 5. Đưa vào context với hậu tố _list
        for s, plist in role_data_lists.items():
            context[f"{s}_list"] = plist
            
        # 6. Alias đặc biệt (Chống lỗi gõ thiếu dấu hoặc sai legacy key)
        if 'ben_vay_list' in context:
            context['tin_dung_list'] = context['ben_vay_list'] # Alias phổ biến
        if 'ben_bao_dam_list' in context:
            context['bao_dam_list'] = context['ben_bao_dam_list'] # Alias phổ biến

        # Helper function for safe filenames
        import re
        import unicodedata
        def clean_filename(name):
            if not name:
                return "document"
            # Loại bỏ dấu tiếng Việt
            s = str(name)
            s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
            s = re.sub(r'[ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ]', 'A', s)
            s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
            s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
            s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
            s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
            s = re.sub(r'[ìíịỉĩ]', 'i', s)
            s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
            s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
            s = re.sub(r'[ÙÚỤỦŨƯỪỨỰỬỮ]', 'U', s)
            s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
            s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
            s = re.sub(r'[đ]', 'd', s)
            s = re.sub(r'[Đ]', 'D', s)
            # Thay thế ký tự không hợp lệ bằng underscore
            s = re.sub(r'[\\/*?:"<>|]', '_', s)
            # Thay thế khoảng trắng bằng underscore và loại bỏ ký tự không phải ASCII
            s = s.replace(" ", "_")
            s = re.sub(r'[^\x00-\x7f]', r'', s) # Loại bỏ các ký tự non-ascii còn lại
            return s

        # Prepare Jinja environment
        jinja_env = Environment()
        jinja_env.filters['format_currency'] = format_currency_filter
        jinja_env.filters['num2words'] = num2words_filter
        jinja_env.filters['dateformat'] = dateformat_filter
        jinja_env.filters['to_roman'] = to_roman_filter

        context['today'] = date.today().strftime('%d/%m/%Y')

        # 3. XỬ LÝ TEMPLATE VÀ SINH FILE
        template_ids = data.get('template_ids', [])
        document_template_id = data.get('template_id')
        
        # Thu thập danh sách templates cần xử lý
        if template_ids:
            templates_to_process = DocumentTemplate.objects.filter(id__in=template_ids)
        elif document_template_id:
            templates_to_process = DocumentTemplate.objects.filter(id=document_template_id)
        else:
            return Response({"error": "No template selected"}, status=status.HTTP_400_BAD_REQUEST)

        if not templates_to_process.exists():
            return Response({"error": "Mẫu tài liệu không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        results = []
        try:
            for document_template in templates_to_process:
                template_path = document_template.file.path
                if not os.path.exists(template_path):
                    continue
                    
                doc = DocxTemplate(template_path)
                doc.render(context, jinja_env=jinja_env)
                
                file_stream = io.BytesIO()
                doc.save(file_stream)
                file_stream.seek(0)
                
                # Tạo tên file output an toàn
                filename = f"{clean_filename(document_template.name)}.docx"
                results.append((filename, file_stream))

            if not results:
                return Response({"error": "Không thể sinh bất kỳ file nào (File mẫu có thể bị thiếu trên server)."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 4. TRẢ VỀ KẾT QUẢ (1 FILE HOẶC ZIP)
            if len(results) == 1:
                filename, file_stream = results[0]
                # Encode filename properly for HTTP header
                from django.utils.encoding import escape_uri_path
                safe_filename = escape_uri_path(filename)
                
                response = FileResponse(file_stream, as_attachment=True, filename=filename)
                response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                return response
            else:
                # Sinh file ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for filename, file_stream in results:
                        zip_file.writestr(filename, file_stream.getvalue())
                
                zip_buffer.seek(0)
                zip_filename = f"{clean_filename(loan_profile.name)}.zip"
                from django.utils.encoding import escape_uri_path
                safe_zip_filename = escape_uri_path(zip_filename)

                response = FileResponse(zip_buffer, as_attachment=True, filename=zip_filename)
                response['Content-Type'] = 'application/zip'
                response['Content-Disposition'] = f'attachment; filename="{safe_zip_filename}"'
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                return response

        except Exception as e:
            print(f"Lỗi sinh file: {e}")
            import traceback
            traceback.print_exc()
            return Response({"error": f"Lỗi sinh file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 10. ViewSets phục vụ Master Data (Universal)
def save_master_field_values(instance, field_values):
    """Generic helper để lưu dynamic field values cho MasterObject"""
    if not field_values:
        return
    
    # 1. Cập nhật bản gốc (Master Data)
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

    # 2. ĐỒNG BỘ: Cập nhật cho các Hồ sơ vay liên quan (Chỉ những hồ sơ DRAFT)
    from .models import LoanProfileObjectLink
    links = LoanProfileObjectLink.objects.filter(master_object=instance, loan_profile__status='DRAFT')
    
    for link in links:
        profile = link.loan_profile
        for key, val in field_values.items():
            try:
                field_obj = Field.objects.get(placeholder_key=key)
                FieldValue.objects.update_or_create(
                    master_object=instance,
                    loan_profile=profile,
                    field=field_obj,
                    defaults={'value': str(val)}
                )
            except Field.DoesNotExist:
                continue

def find_existing_master_object(object_type, field_values):
    """
    Tìm kiếm MasterObject đã tồn tại dựa trên identity_field_key của loại đối tượng đó.
    """
    if not object_type or not field_values:
        return None
        
    try:
        from .models import MasterObjectType, FieldValue
        obj_type_config = MasterObjectType.objects.filter(code=object_type).first()
        if not obj_type_config or not obj_type_config.identity_field_key:
            return None
            
        id_key = obj_type_config.identity_field_key
        id_value = str(field_values.get(id_key, '')).strip()
        
        # CHỈ KHỬ TRÙNG nếu mã định danh có giá trị thực sự (không rỗng, không quá ngắn, không phải placeholder)
        forbidden_identifiers = ['n/a', 'none', 'không có', 'khong co', 'chưa có', 'chua co', '_____']
        is_placeholder = any(f in id_value.lower() for f in forbidden_identifiers)
        
        if not id_value or len(id_value) < 3 or is_placeholder:
            return None
            
        # 2. Tìm kiếm FieldValue khớp với key và value (ở mức Master, loan_profile=None)
        matching_fv = FieldValue.objects.filter(
            master_object__object_type=object_type,
            master_object__deleted_at__isnull=True, # CHỈ TÌM ĐỐI TƯỢNG ACTIVE
            field__placeholder_key=id_key,
            value=id_value,
            loan_profile__isnull=True
        ).first()
        
        return matching_fv.master_object if matching_fv else None
    except Exception as e:
        print(f"Error in find_existing_master_object: {e}")
        return None

    except Exception as e:
        print(f"Error in find_existing_master_object: {e}")
        return None

# --- RELATION VIEWSET ---
class MasterObjectRelationViewSet(viewsets.ModelViewSet):
    queryset = MasterObjectRelation.objects.all().order_by('-created_at')
    serializer_class = MasterObjectRelationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_relation(self, request):
        """API thủ công để tạo quan hệ (dùng cho nút 'Gán quan hệ' ở Frontend)"""
        source_id = request.data.get('source_id')
        target_id = request.data.get('target_id')
        rtype = request.data.get('relation_type', 'OWNER')

        if not source_id or not target_id:
            return Response({"error": "Thiếu source_id hoặc target_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            source = MasterObject.objects.get(id=source_id)
            target = MasterObject.objects.get(id=target_id)
            
            relation, created = MasterObjectRelation.objects.get_or_create(
                source_object=source,
                target_object=target,
                relation_type=rtype
            )
            
            return Response(MasterObjectRelationSerializer(relation).data)
        except MasterObject.DoesNotExist:
            return Response({"error": "Không tìm thấy đối tượng"}, status=status.HTTP_404_NOT_FOUND)

# --- UNIVERSAL ENTITY VIEWSETS ---

class MasterObjectTypeViewSet(viewsets.ModelViewSet):
    queryset = MasterObjectType.objects.all().order_by('code')
    serializer_class = MasterObjectTypeSerializer
    permission_classes = [IsAdminOrManager] 
    # Trong thực tế nên hạn chế quyền sửa đổi cho Admin


class MasterObjectViewSet(viewsets.ModelViewSet):
    queryset = MasterObject.objects.all().order_by('-id')
    serializer_class = MasterObjectSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Xóa hàng loạt đối tượng Master. Chỉ ROOT (superuser) mới có quyền này.
        """
        if not request.user.is_superuser:
            return Response({"error": "Bạn không có quyền thực hiện hành động này."}, status=status.HTTP_403_FORBIDDEN)
        
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "Danh sách ID không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Xóa hờ các đối tượng (Soft Delete)
                deleted_count = MasterObject.objects.filter(id__in=ids).update(deleted_at=timezone.now())
                
                # Log hành động
                log_action(request.user, 'DELETE', 'MasterObject:BULK', 0, f"Xóa hàng loạt {deleted_count} đối tượng (Soft Delete): {ids}")
                
                return Response({"status": "success", "message": f"Đã xóa {deleted_count} đối tượng thành công."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        """Filter by object_type and hide soft-deleted items"""
        queryset = MasterObject.objects.filter(deleted_at__isnull=True).order_by('-id')
        object_types = self.request.query_params.get('object_type', None)
        if object_types:
            codes = [c.strip() for c in object_types.split(',') if c.strip()]
            if codes:
                queryset = queryset.filter(object_type__in=codes)
        return queryset

    def perform_create(self, serializer):
        object_type = self.request.data.get('object_type')
        field_values = self.request.data.get('field_values', {})
        
        # Kiểm tra trùng lặp trước khi tạo
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
        instance = serializer.save(last_updated_by=user)
        field_values = self.request.data.get('field_values', {})
        save_master_field_values(instance, field_values)
        log_action(user, 'UPDATE', f'MasterObject:{instance.object_type}', instance.id, f"Cập nhật dữ liệu gốc")

    def perform_destroy(self, instance):
        o_id = instance.id
        o_type = instance.object_type
        # Soft Delete
        instance.deleted_at = timezone.now()
        instance.save()
        log_action(self.request.user, 'DELETE', f'MasterObject:{o_type}', o_id, f"Xóa hờ dữ liệu gốc")

    @action(detail=False, methods=['get'])
    def check_identity(self, request):
        """
        Kiểm tra nhanh xem một mã định danh đã tồn tại chưa.
        Params: object_type, key, value
        """
        obj_type = request.query_params.get('object_type')
        key = request.query_params.get('key')
        value = request.query_params.get('value')
        
        if not all([obj_type, key, value]):
            return Response({"error": "Missing params"}, status=400)
            
        existing = find_existing_master_object(obj_type, {key: value})
        if existing:
            return Response({
                "exists": True,
                "id": existing.id,
                "display_name": existing.display_name
            })
        
        return Response({"exists": False})

    @action(detail=True, methods=['get'])
    def related_profiles(self, request, pk=None):
        master_obj = self.get_object()
        # Find all profiles linked to this object
        links = LoanProfileObjectLink.objects.filter(master_object=master_obj).select_related('loan_profile')
        profiles = [link.loan_profile for link in links]
        
        data = []
        for p in profiles:
            form_name = p.form_view.name if p.form_view else 'Mặc định'
            data.append({
                'id': p.id,
                'name': p.name,
                'created_at': p.created_at,
                'form_name': form_name
            })
        return Response(data)

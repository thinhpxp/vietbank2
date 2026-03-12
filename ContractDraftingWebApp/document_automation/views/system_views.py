from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django_filters.rest_framework import DjangoFilterBackend
import os
import logging

from ..models import AuditLog, AdminNotification, NotificationRead, SystemConfig, Role
from ..serializers import (
    UserSerializer, GroupSerializer, PermissionSerializer,
    RegistrationSerializer, PasswordChangeSerializer,
    AuditLogSerializer, AdminNotificationSerializer, SystemConfigSerializer
)
from ..permissions import IsAdminOrManager, IsSuperUser

logger = logging.getLogger(__name__)

# --- HELPER GHI LOG ---
def format_changes(changed_dict, target_model=None):
    """
    Chuyển đổi dictionary thay đổi thành văn bản thân thiện:
    Input: {'field_key': {'from': old_val, 'to': new_val}}
    Output: "Họ tên: A -> B, Số điện thoại: 1 -> 2"
    """
    if not changed_dict or not isinstance(changed_dict, dict):
        return ""
    
    from ..models import Field
    results = []
    
    # Lấy cache danh sách fields để tránh nhiều query
    field_keys = list(changed_dict.keys())
    fields_map = {f.placeholder_key: f.label for f in Field.objects.filter(placeholder_key__in=field_keys)}
    
    for key, diff in changed_dict.items():
        label = fields_map.get(key, key) # Fallback về key nếu không tìm thấy label
        old_val = diff.get('from', '')
        new_val = diff.get('to', '')
        
        # Định dạng giá trị (ví dụ: None -> rỗng)
        old_val = "N/A" if old_val is None else old_val
        new_val = "N/A" if new_val is None else new_val
        
        results.append(f"{label}: {old_val} -> {new_val}")
    
    return ", ".join(results)

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
        logger.error(f"Lỗi ghi AuditLog: {e}")

# --- SIGNALS CHO LOGIN/LOGOUT ---
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_action(user, 'LOGIN', 'User', user.id, f"Người dùng {user.username} đăng nhập")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_action(user, 'LOGOUT', 'User', user.id, f"Người dùng {user.username} đăng xuất")

# --- AUTH & PROFILE VIEWS ---
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

# --- SYSTEM CONFIG & LOGO ---
class LogoUploadView(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request):
        if 'logo' not in request.FILES:
            return Response({"error": "Không tìm thấy file logo."}, status=status.HTTP_400_BAD_REQUEST)
        logo_file = request.FILES['logo']
        if logo_file.size > 2 * 1024 * 1024:
            return Response({"error": "File quá lớn (Tối đa 2MB)."}, status=status.HTTP_400_BAD_REQUEST)
        ext = os.path.splitext(logo_file.name)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
            return Response({"error": "Định dạng file không được hỗ trợ."}, status=status.HTTP_400_BAD_REQUEST)
        if not logo_file.content_type.startswith('image/'):
             return Response({"error": "File tải lên không phải là ảnh hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)

        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"branding/logo_{timestamp}{ext}"
        path = default_storage.save(safe_filename, ContentFile(logo_file.read()))
        logo_url = f"{settings.MEDIA_URL}{path}"
        if not logo_url.startswith('http'):
            request_host = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
            logo_url = f"{protocol}://{request_host}{logo_url}"
        log_action(request.user, 'UPLOAD', 'SystemConfig', None, f"Admin đã tải lên logo mới: {path}")
        return Response({"status": "success", "logoUrl": logo_url, "message": "Tải lên logo thành công!"})

class SystemConfigView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET': return [AllowAny()]
        return [IsSuperUser()]
    def get(self, request):
        config = SystemConfig.get_config()
        serializer = SystemConfigSerializer(config)
        return Response(serializer.data)
    def post(self, request):
        config = SystemConfig.get_config()
        serializer = SystemConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            log_action(request.user, 'UPDATE', 'SystemConfig', 1, "Admin đã cập nhật cấu hình giao diện")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- USER, GROUP, PERMISSION ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile').prefetch_related('groups').order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
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
    queryset = Permission.objects.exclude(
        content_type__app_label__in=['sessions', 'contenttypes', 'admin']
    ).exclude(
        content_type__model__in=['systemconfig', 'auditlog', 'notificationread', 'userprofile', 'loanprofileobjectlink']
    ).select_related('content_type').order_by('content_type__model', 'codename')
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminOrManager]
    pagination_class = None
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(codename__icontains=search) | Q(content_type__app_label__icontains=search) | Q(content_type__model__icontains=search))
        return queryset

# --- AUDIT LOG ---
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_model', 'target_id', 'action', 'user']
    search_fields = ['details', 'target_id', 'target_model']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']

# --- NOTIFICATIONS ---
class AdminNotificationViewSet(viewsets.ModelViewSet):
    queryset = AdminNotification.objects.all().order_by('-created_at')
    serializer_class = AdminNotificationSerializer
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            now = timezone.now()
            qs = qs.filter(is_active=True).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        return qs
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        log_action(self.request.user, 'CREATE', 'AdminNotification', None, f"Tạo thông báo: {serializer.validated_data.get('title')}")
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        read_obj, created = NotificationRead.objects.get_or_create(notification=notification, user=request.user)
        return Response({"status": "Success", "created": created})
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        now = timezone.now()
        notifications = AdminNotification.objects.filter(is_active=True).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        read_ids = NotificationRead.objects.filter(user=self.request.user).values_list('notification_id', flat=True)
        unread = notifications.exclude(id__in=read_ids).count()
        return Response({"unread_count": unread})

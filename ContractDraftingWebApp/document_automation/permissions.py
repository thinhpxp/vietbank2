from rest_framework import permissions

class IsAdminOrManager(permissions.DjangoModelPermissions):
    """
    Custom permission — Phân quyền theo RBAC:
    1. Superuser (ROOT): Toàn quyền, bypass mọi kiểm tra.
    2. Staff (Quản trị) và User thường: Phải có quyền tường minh trong Group.
       - GET    -> Requires 'view_model'
       - POST   -> Requires 'add_model'
       - PUT/PATCH -> Requires 'change_model'
       - DELETE -> Requires 'delete_model'
    """
    
    # Override perms_map to ensure GET requires 'view' permission
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        # Chỉ ROOT (superuser) mới được bypass tất cả kiểm tra RBAC.
        # Staff (is_staff) phải có quyền tường minh trong Group.
        if request.user.is_superuser:
            return True

        # Kiểm tra quyền theo DjangoModelPermissions (dựa trên Group)
        return super().has_permission(request, view)

class ReadOnlyMetadataOrAdmin(permissions.BasePermission):
    """
    - GET: Mọi user đã đăng nhập đều được xem metadata.
    - Write (POST/PUT/PATCH/DELETE): Chỉ ROOT (superuser) hoặc staff có quyền tường minh.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Chỉ ROOT được tự động ghi. Staff cần quyền tường minh (không bypass ở đây).
        return request.user.is_superuser

class IsSuperUser(permissions.BasePermission):
    """
    Chỉ superuser (ROOT) mới được phép truy cập.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

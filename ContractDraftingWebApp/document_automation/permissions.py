from rest_framework import permissions

class IsAdminOrManager(permissions.DjangoModelPermissions):
    """
    Custom permission to allow access if:
    1. User is Staff or Superuser (Full Admin Access).
    2. OR User has specific Action-based permissions (Smart RBAC).
       - GET -> Requires 'view_model'
       - POST -> Requires 'add_model'
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
        # 1. Standard Admin Access (Legacy/Technical)
        # Staff and Superusers bypass granular checks (keep legacy behavior)
        if request.user.is_staff or request.user.is_superuser:
            return True

        # 2. Smart Access (RBAC)
        # Rely on DjangoModelPermissions to check auth + specific action permission
        return super().has_permission(request, view)

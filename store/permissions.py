from rest_framework.permissions import BasePermission, SAFE_METHODS, DjangoModelPermissions

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit an object.
    """
    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)
    
class FullDjangoModelPermissions(DjangoModelPermissions):
    """
    Custom permission to allow all actions for admins and read-only for others.
    """
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']



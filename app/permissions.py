from rest_framework import permissions

class IsTutee(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            is_tutee = request.user.tutee_profile
            return True
        except Exception as e:
            return False

class IsTutor(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            is_tutor = request.user.tutor_profile
            return True
        except Exception as e:
            return False

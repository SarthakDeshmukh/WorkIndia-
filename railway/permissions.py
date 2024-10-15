
from rest_framework.permissions import BasePermission
from django.conf import settings

class IsAdminWithAPIKey(BasePermission):
    """
    Allows access only to admin users with a valid API key.
    """

    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-KEY')
        return (
            request.user and 
            request.user.is_staff and 
            api_key == settings.ADMIN_API_KEY
        )
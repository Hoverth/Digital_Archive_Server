from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AuthenticationForm


class CustomAdminSite(AdminSite):
    """
    App-specific admin site implementation
    """

    login_form = AuthenticationForm

    site_header = 'Digital Archive Server'

    def has_permission(self, request):
        """
        Checks if the current user has access.
        """
        return request.user.is_active


site = CustomAdminSite(name='customadmin')
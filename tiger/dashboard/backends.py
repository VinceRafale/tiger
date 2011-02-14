from django.contrib.auth.models import User

class DashboardAccessBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, email=None, password=None, site=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and any([user.is_superuser, user == site.account.user, user == site.user]):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

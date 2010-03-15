from django.contrib.auth.models import User

class DashboardAccessBackend(object):
    def authenticate(self, username=None, password=None, site=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and (user.is_superuser or user == site.account.user):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

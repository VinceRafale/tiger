from django.contrib.auth.models import User
from tiger.sales.models import Account

class ResellerBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            try:
                account = user.get_profile()
            except Account.DoesNotExist:
                is_manager = False
            else:
                is_manager = account.manager
            if user.check_password(password) and is_manager:
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

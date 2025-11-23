from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class UsernameOrEmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        user = User.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username) | Q(phone__iexact=username)
        ).first()

        if user and user.check_password(password) and user.is_active:
            return user
        return None


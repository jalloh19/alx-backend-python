from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class.
    Extends the default JWTAuthentication to add custom validation.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        """
        Get the user from the validated token.
        """
        try:
            user_id = validated_token.get('user_id')
        except KeyError:
            raise AuthenticationFailed(
                _('Token contained no recognizable user identification')
            )

        from chats.models import User
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found'))

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'))

        return user

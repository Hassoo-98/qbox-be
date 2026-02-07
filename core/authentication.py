from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # First, try to get token from cookies
        token = request.COOKIES.get("access_token")
        
        # If not found in cookies, try Authorization header
        if not token:
            auth_header = request.headers.get('Authorization') or request.headers.get('authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return None
            
        try:
            validated_token = self.get_validated_token(token)
        except (InvalidToken, TokenError) as e:
            print("JWT VALIDATION ERROR:", e)
            return None

        user_id = validated_token.get('user_id')
        if user_id is None:
            return None
            
        try:
            # Try to get user by id (handles both int and UUID)
            user = User._default_manager.get(pk=user_id)
        except (User.DoesNotExist, ValueError):
            # ValueError happens when UUID string is passed to integer field
            # Try to get by UUID
            try:
                user = User._default_manager.get(id=user_id)
            except (User.DoesNotExist, ValueError):
                return None

        return (user, token)

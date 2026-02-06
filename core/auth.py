from rest_framework import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .authentication import CookieJWTAuthentication
from .serializers import MeSerializer
class MeView(APIView):
    authentication_classes=[CookieJWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        return Response({
            "id":request.user.id,
            "username":request.user.username,
            "roles":request.user.roles,
            "permissions":request.user.permissions
        })


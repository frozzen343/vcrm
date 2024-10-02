from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import UserListSerializer, UserSerializer


class UserDetails(APIView):
    """
    List all permissions for a request user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserListAPIView(ListAPIView):
    """
    User list view
    """
    queryset = User.objects.filter(is_active=True).order_by('-last_name').all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        if (not self.request.user.has_perm('perms.view_other_users_tasks')
                or not self.request.user.has_perm('perms.change_performer')):
            queryset = User.objects.filter(id=self.request.user.id)
        return queryset

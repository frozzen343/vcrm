from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.serializers import UserListSerializer


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
        if not self.request.user.has_perm('perms.view_other_users_tasks'):
            queryset = User.objects.filter(id=self.request.user.id)
        return queryset

from django.urls import path
from django.contrib.auth.views import LogoutView

from users.views import (UserLoginView,
                         UserProfileView,
                         UserCreateView,
                         UserListView,
                         UserEditView,
                         UserDeleteView,
                         UserChengePass,
                         background,
                         group_delete,
                         group_add)


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='profile'),
    path('background/', background, name='background'),
    path('user_list/', UserListView.as_view(), name='user_list'),
    path('user_list/create/', UserCreateView.as_view(), name='user_create'),
    path('user_list/<int:pk>/', UserEditView.as_view(), name='user_edit'),
    path('user_list/<int:pk>/del/', UserDeleteView.as_view(), name='user_del'),
    path('user_list/<int:pk>/pass/',
         UserChengePass.as_view(),
         name='user_changepass'),
    path('user_list/<int:user_id>/groups/<int:group_id>/add/',
         group_add,
         name='group_add'),
    path('user_list/<int:user_id>/groups/<int:group_id>/del/',
         group_delete,
         name='group_del'),
]

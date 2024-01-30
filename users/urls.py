from django.urls import path
from django.contrib.auth.views import LogoutView

import users.views as views
import users.views_api as views_api


urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile'),
    path('background/', views.background, name='background'),
    path('user_list/', views.UserListView.as_view(), name='user_list'),
    path('user_list/create/', views.UserCreateView.as_view(),
         name='user_create'),
    path('user_list/<int:pk>/', views.UserEditView.as_view(),
         name='user_edit'),
    path('user_list/<int:pk>/del/', views.UserDeleteView.as_view(),
         name='user_del'),
    path('user_list/<int:pk>/pass/',
         views.UserChangePass.as_view(),
         name='user_changepass'),
    path('user_list/<int:user_id>/groups/<int:group_id>/add/',
         views.group_add,
         name='group_add'),
    path('user_list/<int:user_id>/groups/<int:group_id>/del/',
         views.group_delete,
         name='group_del'),

    path('api/v1/user_list', views_api.UserListAPIView.as_view(),
         name='api_user_list'),
]

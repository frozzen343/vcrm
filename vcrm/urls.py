"""vcrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

# import vcrm.views_api as views_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('account/', include('users.urls')),
    path('tasks/', include('tasks.urls')),
    path('clients/', include('clients.urls')),
    path('reports/', include('reports.urls')),
    path('mail/', include('mail.urls')),
    path('settings/', include('settings.urls')),

    # path('settings/api/v1/test', views_api.TestAPIView.as_view(),
    #         name='tests'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler400 = 'main.views.handler400'
handler403 = 'main.views.handler403'
handler404 = 'main.views.handler404'
handler500 = 'main.views.handler500'


if settings.DEBUG:
    urlpatterns = [
        # path('__debug__/', include('debug_toolbar.urls')),
        # path('silk/', include('silk.urls', namespace='silk')),
    ] + urlpatterns

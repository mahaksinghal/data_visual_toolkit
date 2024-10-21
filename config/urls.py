"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from uploads import views as ufv
from selected_file import views as sfv


urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),

    # uploaded file
    path('',ufv.upload_file, name='upload_file'),
    path('data_view/', ufv.data_view, name='data_view'),
    path('generate_graphs/', ufv.generate_graphs, name='generate_graphs'),
    path('files/', ufv.file_list, name='file_list'),

    # selected file
    path('files/<int:file_id>/', sfv.file_detail, name='file_detail'),
    path('files/<int:file_id>/select/', sfv.select_file, name='select_file'),
    path('files/select_file/', sfv.select_file_view, name='select_file_view'),
    path('files/generated_graphs/', sfv.generated_graphs, name='generated_graphs'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
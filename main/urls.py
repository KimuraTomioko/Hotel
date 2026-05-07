"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='app/index.html'), name='home'),
    path('auth/', TemplateView.as_view(template_name='app/auth.html'), name='auth_page'),
    path('cabinet/', TemplateView.as_view(template_name='app/cabinet.html'), name='cabinet'),
    path('hotels/new/', TemplateView.as_view(template_name='app/hotel_form.html'), name='hotel_form'),
    path('admin/', admin.site.urls),
    path('api/', include('app.urls') )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

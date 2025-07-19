"""
URL configuration for cinematch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from movies.forms import CustomUserCreationForm
from django.views.generic import CreateView
from django.conf import settings
from django.conf.urls.static import static

def logout_view(request):
    logout(request)
    return redirect('movies:index')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls', namespace='movies')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', CreateView.as_view(
        template_name='registration/signup.html',
        form_class=CustomUserCreationForm,
        success_url='/'
    ), name='signup'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

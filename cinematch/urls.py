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
from movies.forms import CustomUserCreationForm, CustomAuthenticationForm
from django.views.generic import CreateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import messages
from django.urls import reverse_lazy
from django.conf.urls.i18n import i18n_patterns

def logout_view(request):
    logout(request)
    return redirect('movies:index')

class CustomSignUpView(CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created successfully for {username}! Please login to continue.')
        return response

# Language-independent URLs (like admin and language switching)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Language-dependent URLs
urlpatterns += i18n_patterns(
    path('', include('movies.urls', namespace='movies')),
    path('login/', auth_views.LoginView.as_view(authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', CustomSignUpView.as_view(), name='signup'),
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

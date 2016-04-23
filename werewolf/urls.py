"""werewolf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import django.views.static
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^', include('registration.backends.simple.urls')),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^about/$', views.about, name='about'),
    url(r'^game/(?P<name>\w+)', views.game, name='game'),
    url(r'^ready/(?P<game_name>\w+)/(?P<user_id>\w+)$', views.ready, name='ready'),
    url(r'^start/(?P<game_name>\w+)$', views.start, name='start'),
    url(r'^create/$',
        login_required(views.GameCreate.as_view()),
        name='create'),
    url(
        r'^static/(?P<path>.*)$',
        django.views.static.serve,
        name='static',
        kwargs={'document_root', settings.STATIC_ROOT},
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

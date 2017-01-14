"""weather URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin
import reminder.views as reminder_views

urlpatterns = [
    url(r'^$', reminder_views.manage),
    url(r'^admin/', admin.site.urls),
    url(r'^del_reminder/', reminder_views.del_reminder),
    url(r'^test_email/', reminder_views.test_email),
    url(r'^secret_trigger/', reminder_views.secret_trigger),
    url(r'^accounts/', include('allauth.urls')),
]

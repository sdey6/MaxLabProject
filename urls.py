"""MaxLabProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

from video_app.views import (
    account_view,
    home_screen_view,
    registration_view,
    logout_view,
    login_view,
    verification_view,
    request_password_reset_email,
    reset_user_password,
    experiments_view,
    create_room_view,
    download_view,
    editExp
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('transcription/', include('transcription_app.urls')),
    path('', home_screen_view, name="home"),
    path('register/', registration_view, name="register"),
    path('logout/', logout_view, name="logout"),
    path('login/', login_view, name="login"),
    path('account/', account_view, name="account"),
    path('activate/<email>/<token>', verification_view, name="activate"),
    path('request-reset-link/',request_password_reset_email,name="request-reset-link"),
    path('experiments/',experiments_view,name="experiments"),
    path('reset-user-password/<email>/<token>',reset_user_password,name="reset-user-password"),
    path('create-room/',create_room_view,name="create-room"),
    path('download/<str:type>/<str:roomid>',download_view,name="download"),
    path('experiments/<str:message>',experiments_view,name="experiments_failed"),
    path('edit_room/<str:room_id>',editExp,name="edit_room"),

]

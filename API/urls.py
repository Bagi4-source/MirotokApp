from django.conf.urls.static import static
from django.urls import include, path, re_path
from rest_framework import routers

from Backend import settings
from . import views
from . import admin_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('login/', views.login, name='Login'),
    path('logout/', views.logout, name='Logout'),
    path('checkCode/', views.check_code, name='CheckCode'),
    path('register/', views.register, name='Register'),
    path('get_test/', views.get_test, name='GetTest'),
    path('set_fbid/', views.set_fbid, name='SetFBid'),
    path('get_me/', views.get_me, name='GetMe'),
    path('set_test/', views.set_test, name='SetTest'),
    path('get_main/', views.get_main, name='GetMain'),
    path('get_results/', views.get_results, name='GetResults'),
    path('get_products/', views.get_products, name='GetProducts'),
    path('buy/', views.buy, name='Buy'),
    path('validate_buy/', views.validate_buy, name='ValidateBuy'),
    path('add_diary/', views.add_diary, name='AddDiary'),
    path('get_my_diary/', views.get_my_diary, name='GetMyDiary'),
    path('set_avatar/', views.set_avatar, name='SetAvatar'),
    path('get_avatar/', views.get_avatar, name='GetAvatar'),
]
admin_urls = [
    path('get_users/', admin_views.get_users, name='GetUsers'),
    path('get_user/', admin_views.get_user, name='GetUser'),
    path('send_messages_all/', admin_views.send_messages_all, name='SendMessageAll'),
    path('send_message/', admin_views.send_message, name='SendMessage'),
    path('get_all_messages/', admin_views.get_all_messages, name='GetAllMessages'),
    path('get_user_diary/', admin_views.get_user_diary, name='GetUserDiary'),
    path('get_user_results/', admin_views.get_user_results, name='GetUserResults'),
]

urlpatterns.extend(admin_urls)
urlpatterns.extend(staticfiles_urlpatterns())

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views

app_name = 'chat'  

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.index, name='chat_home'),
    path('chat/', views.chat_home, name='chat_home'),  
    path('chat/<str:room_name>/', views.room, name='room'),  

]
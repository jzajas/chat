from django.urls import path
from . import views


# urlpatterns = [
#     # path("", views.index, name="login"),
#     path("<str:room_name>/", views.room, name="room"),

#     path('register/', views.register_view, name='register'),
#     path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
#     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),


#     # path("", views.chatPage, name="chat-page"),


#     # login-section
#     # path("auth/login/", LoginView.as_view(template_name="chat/LoginPage.html"), name="login-user"),
#     # path("auth/logout/", LogoutView.as_view(), name="logout-user"),
# ]

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.chat_home, name='chat_home'),
    path('room/<str:room_name>/', views.chat_room, name='chat_room'),

    path('', views.index, name='index'),  # Homepage
    path('chat/', views.chat_home, name='chat_home'),  # Chat rooms list
    # path('chat/<str:room_name>/', views.chat_room, name='room'),  # Individual chat room
]
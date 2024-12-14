from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),

    path('register/', views.register_view, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),


    # path("", views.chatPage, name="chat-page"),


    # login-section
    # path("auth/login/", LoginView.as_view(template_name="chat/LoginPage.html"), name="login-user"),
    # path("auth/logout/", LogoutView.as_view(), name="logout-user"),
]
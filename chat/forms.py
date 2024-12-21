from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import NewUser

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
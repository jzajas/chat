from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django import forms
from chat.models.user import NewUser

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = NewUser
        fields = ('username',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('chat:chat_home')  # Updated with namespace
        else:
            messages.error(request, 'Error in registration. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('chat:chat_home')  # Updated with namespace
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('chat:login')  # Updated with namespace


def index(request):
    return render(request, 'chat/chat_home.html')


@login_required
def chat_home(request):
    # You could add context here if needed, like a list of active rooms
    context = {
        'default_rooms': ['general', 'tech']  # Example of additional context
    }
    return render(request, 'chat/chat_home.html', context)

@login_required
def room(request, room_name):
    # Validate room_name if needed
    if not room_name:
        return redirect('chat:chat_home')
        
    return render(request, 'chat/chat_room.html', {
        'room_name': room_name
    })


@login_required
def display_username(request):
    # Pass the logged-in user's username to the template
    context = {
        'username': request.user.username,
    }
    return render(request, 'chat/base.html', context)
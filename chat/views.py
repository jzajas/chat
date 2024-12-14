from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm

def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')  # Changed from 'chat_dashboard' to 'index'
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
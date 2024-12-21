# from django.shortcuts import render, redirect
# from django.contrib.auth import login, logout, authenticate
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
# from .forms import UserRegistrationForm



# def index(request):
#     return render(request, "chat/index.html")

# @login_required
# def room(request, room_name):
#     return render(request, "chat/room.html", {"room_name": room_name})

# def register_view(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('index')  # Changed from 'chat_dashboard' to 'index'
#     else:
#         form = UserRegistrationForm()
    
#     return render(request, 'registration/register.html', {'form': form})


# def index(request):
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(request, username = username, password =password  )
     
#         if user is not None:
#             login(request , user)
#             return redirect('/chat/home')    
#         else:
#             messages.info(request, 'invalid username or password')
#             return redirect("/")

# def logout_view(request):
#     logout(request)
#     return redirect('/registration/login')    

# def register_view(request):
#     form = UserCreationForm()
#     return render(request, "registration/register.html", {"form": form})



from django.shortcuts import render, redirect 
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib import messages

User = get_user_model()

# Create your views here.
def register_view(request):
    if request.method == "POST": 
        form = UserCreationForm(request.POST) 
        if form.is_valid(): 
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('chat_home')
        else:
                messages.error(request, 'Error in registration. Please correct the errors below.')
    else:
        form = UserCreationForm()

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
                return redirect('chat_home')  # Replace with your chat homepage URL name
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login') 


def index(request):
    return render(request, 'chat/index.html')


def chat_home(request):
    return render(request, 'chat/chat_home.html')


def chat_room(request, room_name):
    return render(request, 'chat/chat_room.html', {
        'room_name': room_name
    })
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, LoginForm

# Create your views here.

def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/registration.html', {
        "form": form
    })

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username_email = form.cleaned_data["username_email"]
            password = form.cleaned_data["password"]
            
            user = authenticate(
                request,
                username=username_email,
                password=password
            )

            if user is not None:
                login(request, user)

                return redirect("home")
            else:
                form.add_error(
                    None,
                    "Неверный логин ли пароль"
                )
    else:
        form = LoginForm()
        
    return render(request, 'accounts/login.html', {
        "form": form
    })
    
def logout_view(request):

    logout(request)

    return redirect("home")

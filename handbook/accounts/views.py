from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, LoginForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


# Create your views here.

def registration(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method != "POST":
        return render(request, 'accounts/registration.html', {
            "form": RegistrationForm()
        })
    
    form = RegistrationForm(request.POST)

    if not form.is_valid():
        return render(request, 'accounts/registration.html', {
            "form": form
        })

    user = form.save()
    login(request, user)
    return redirect("home")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method != "POST":
        return render(request, 'accounts/login.html', {"form": LoginForm()})

    form = LoginForm(request.POST)

    if not form.is_valid():
        return render(request, 'accounts/login.html', {"form": form})

    username_email = form.cleaned_data["username_email"]
    password = form.cleaned_data["password"]
    user = authenticate(request, username=username_email, password=password)

    if user is None:
        form.add_error(None, "Неверный логин или пароль")
        return render(request, 'accounts/login.html', {"form": form})

    login(request, user)
    return redirect("home")



@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")

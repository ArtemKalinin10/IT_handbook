from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.db.models import Count, Q
from education.models import CourseStudent, Homework, Course
from .forms import RegistrationForm, LoginForm, ProfileSettingsForm, PasswordSettingsForm
from django.contrib.auth.decorators import login_required

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

@login_required
def profile(request):
    user = request.user
    
    courses = Course.objects.filter(course_students__student=user).annotate(
        all_homeworks_for_course = Count("homeworks",
                                         distinct=True),
        all_submissions_for_course = Count("homeworks__submissions__homework",
                                           filter=Q(homeworks__submissions__student=user),
                                           distinct=True)
    )
    
    total_homeworks = Homework.objects.filter(course__course_students__student=user).count()
    
    courses_count = courses.count()
    submissions_count = user.submissions.values("homework").distinct().count()
    homeworks_percent = (submissions_count / total_homeworks * 100 if total_homeworks else 0)
    
    stats_for_courses = []
    for course in courses:
        course_percent = (
            course.all_submissions_for_course / course.all_homeworks_for_course * 100
            if course.all_homeworks_for_course else 0
        )
        
        stats_for_courses.append({
            "title": course.title,
            "all_homeworks_for_course": course.all_homeworks_for_course,
            "all_submissions_for_course": course.all_submissions_for_course,
            "course_percent": int(course_percent)
        })

    return render(request, "accounts/profile.html", {
        "all_courses": courses_count,
        "submissions": submissions_count,
        "homeworks_percent": int(homeworks_percent),
        "stats_for_courses": stats_for_courses
    })

@login_required
def settings_view(request):
    profile_form = ProfileSettingsForm(instance=request.user)
    password_form = PasswordSettingsForm(user=request.user)

    return render(request, "accounts/settings.html", {
        "profile_form": profile_form,
        "password_form": password_form,
    })
    
@login_required
def settings_profile(request):
    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()

    return redirect("settings")

@login_required
def settings_password(request):
    if request.method == "POST":
        form = PasswordSettingsForm(request.user, request.POST)

        if form.is_valid():
            form.save()
    return redirect("settings")


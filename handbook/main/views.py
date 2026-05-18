from django.shortcuts import render
from education.models import Course

# Create your views here.

def index(request):
    all_courses = Course.objects.all()
    
    return render(request, 'main/index.html', {
        "all_courses": all_courses
    })
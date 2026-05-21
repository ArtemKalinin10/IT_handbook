from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson, ProgressStatus, Task, UserProgress


def attach_single_lesson_progress(lesson, completed_task_ids):
    lesson_tasks = list(lesson.tasks.all())

    lesson.total_tasks = len(lesson_tasks)
    lesson.completed_tasks = sum(
        1 for task in lesson_tasks
        if task.id in completed_task_ids
    )

    if lesson.total_tasks:
        lesson.progress_percent = int(
            lesson.completed_tasks * 100 / lesson.total_tasks
        )
    else:
        lesson.progress_percent = 0


def attach_lesson_progress(course, completed_task_ids):
    for module in course.modules.all():
        for lesson in module.lessons.all():
            attach_single_lesson_progress(lesson, completed_task_ids)


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.prefetch_related(
        "modules__lessons__tasks"
        ),
        slug=slug
    )

    if request.user.is_authenticated:
        completed_task_ids = set(
            UserProgress.objects.filter(
                user=request.user,
                status=ProgressStatus.COMPLETED,
                task__lesson__module__course=course
            ).values_list("task_id", flat=True)
        )
    else:
        completed_task_ids = set()

    attach_lesson_progress(course, completed_task_ids)

    return render(request, "education/course_detail.html", {
        "course": course
    })

def lesson_detail(request, course_slug, lesson_slug):

    lesson = get_object_or_404(
        Lesson.objects
        .select_related(
            "module",
            "module__course"
        )
        .prefetch_related(
            "blocks",
            "tasks",
            "module__course__modules__lessons__tasks"
        ),
        slug=lesson_slug,
        module__course__slug=course_slug
    )
    if request.user.is_authenticated:
        completed_task_ids = set(
            UserProgress.objects.filter(
                user=request.user,
                status=ProgressStatus.COMPLETED,
                task__lesson__module__course=lesson.module.course
            ).values_list("task_id", flat=True)
        )
    else:
        completed_task_ids = set()

    attach_lesson_progress(lesson.module.course, completed_task_ids)
    attach_single_lesson_progress(lesson, completed_task_ids)

    return render(
        request,
        "education/lesson_detail.html",
        {"lesson": lesson}
    )

def task_detail(request, course_slug, lesson_slug, task_slug):
    task = get_object_or_404(
        Task.objects
        .select_related(
            "lesson",
            "lesson__module",
            "lesson__module__course",
        )
        .prefetch_related(
            "lesson__tasks",
            "blocks",
            "blocks__hint",
            "blocks__hint__blocks"
        ),
        slug=task_slug,
        lesson__slug=lesson_slug,
        lesson__module__course__slug=course_slug,
    )
    
    submissions = task.submissions.order_by("-created_at")

    return render(request, "education/task.html",
                  {"task": task,
                   "submissions": submissions
                   }
    )



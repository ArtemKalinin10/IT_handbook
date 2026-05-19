from django.contrib import admin

from .models import (
    Course,
    Lesson,
    LessonContentBlock,
    Module,
    Submission,
    Task,
    TaskContentBlock,
    TaskHint,
    TaskHintContentBlock,
    UserProgress,
)

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ("title", "order", "execution_time_limit", "size_limit")
    ordering = ("order",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "order")
    ordering = ("order",)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ("title", "order")
    ordering = ("order",)

class ContentBlockInline(admin.TabularInline):
    model = LessonContentBlock
    extra = 1
    fields = ("type", "content", "order")
    ordering = ("order",)


class TaskContentBlockInline(admin.TabularInline):
    model = TaskContentBlock
    extra = 1
    fields = ("type", "content", "hint", "order")
    autocomplete_fields = ("hint",)
    ordering = ("order",)

    
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "lesson",
        "order",
        "execution_time_limit",
        "size_limit",
    )
    list_filter = ("lesson",)
    search_fields = ("title", "lesson__title")
    ordering = ("lesson", "order")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TaskContentBlockInline]
    fields = (
        "lesson",
        "title",
        "slug",
        "order",
        "execution_time_limit",
        "size_limit",
        "starter_code",
    )


class TaskHintContentBlockInline(admin.TabularInline):
    model = TaskHintContentBlock
    extra = 1
    fields = ("type", "content", "order")
    ordering = ("order",)


@admin.register(TaskHint)
class TaskHintAdmin(admin.ModelAdmin):
    list_display = ("__str__", "task", "order")
    list_filter = ("task__lesson",)
    search_fields = ("task__title",)
    ordering = ("task", "order")
    inlines = [TaskHintContentBlockInline]
    autocomplete_fields = ("task",)
    fields = ("task", "order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order")
    list_filter = ("module",)
    search_fields = ("title",)
    ordering = ("module", "order")
    inlines = [TaskInline, ContentBlockInline]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title",)
    ordering = ("course", "order")
    inlines = [LessonInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title",)
    ordering = ("title",)
    inlines = [ModuleInline]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "task", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "task__title")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "task", "status", "completed_at")
    list_filter = ("status", "task")
    search_fields = ("user__username", "task__title")
    readonly_fields = ("completed_at",)
    ordering = ("-completed_at",)
    

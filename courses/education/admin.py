from django.contrib import admin
from .models import (
    Course,
    CourseTeacher,
    CourseStudent,
    Homework,
    HomeworkTeacher,
    Submission,
)


class CourseTeacherInline(admin.TabularInline):
    model = CourseTeacher
    extra = 1


class CourseStudentInline(admin.TabularInline):
    model = CourseStudent
    extra = 1


class HomeworkTeacherInline(admin.TabularInline):
    model = HomeworkTeacher
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "get_teachers", "get_students")
    search_fields = ("title",)
    inlines = (CourseTeacherInline, CourseStudentInline)

    @admin.display(description="Teachers")
    def get_teachers(self, obj):
        return ", ".join(
            obj.course_teachers.values_list("teacher__username", flat=True)
        )

    @admin.display(description="Students")
    def get_students(self, obj):
        return ", ".join(
            obj.course_students.values_list("student__username", flat=True)
        )


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course", "get_teachers")
    search_fields = ("name", "course__title")
    list_filter = ("course",)
    inlines = (HomeworkTeacherInline,)

    @admin.display(description="Teachers")
    def get_teachers(self, obj):
        return ", ".join(
            obj.homework_teachers.values_list("teacher__username", flat=True)
        )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "homework", "get_course", "student", "checked_by", "grade", "created_at")
    search_fields = (
        "homework__name",
        "homework__course__title",
        "student__username",
        "checked_by__username",
    )
    list_filter = ("homework__course", "checked_by", "created_at")

    @admin.display(description="Course")
    def get_course(self, obj):
        return obj.homework.course


@admin.register(CourseTeacher)
class CourseTeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "teacher")
    search_fields = ("course__title", "teacher__username")
    list_filter = ("course",)


@admin.register(CourseStudent)
class CourseStudentAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "student")
    search_fields = ("course__title", "student__username")
    list_filter = ("course",)


@admin.register(HomeworkTeacher)
class HomeworkTeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "homework", "teacher", "get_course")
    search_fields = ("homework__name", "teacher__username", "homework__course__title")
    list_filter = ("homework__course",)

    @admin.display(description="Course")
    def get_course(self, obj):
        return obj.homework.course

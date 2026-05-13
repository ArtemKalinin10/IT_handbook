from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Course(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class CourseTeacher(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_teachers",
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_teacher_links",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "teacher"],
                name="unique_course_teacher",
            )
        ]

    def clean(self):
        if not self.teacher.groups.filter(name="Teacher").exists():
            raise ValidationError({
                "teacher": "Пользователь должен состоять в группе Teacher."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course} - {self.teacher}"


class CourseStudent(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_students",
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_student_links",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "student"],
                name="unique_course_student",
            )
        ]

    def clean(self):
        if not self.student.groups.filter(name="Student").exists():
            raise ValidationError({
                "student": "Пользователь должен состоять в группе Student."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course} - {self.student}"


class Homework(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="homeworks",
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class HomeworkTeacher(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="homework_teachers",
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homework_teacher_links",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["homework", "teacher"],
                name="unique_homework_teacher",
            )
        ]

    def clean(self):
        if not self.teacher.groups.filter(name="Teacher").exists():
            raise ValidationError({
                "teacher": "Пользователь должен состоять в группе Teacher."
            })

        if not CourseTeacher.objects.filter(
            course=self.homework.course,
            teacher=self.teacher,
        ).exists():
            raise ValidationError({
                "teacher": "Этот преподаватель не привязан к курсу данной домашки."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.homework} - {self.teacher}"


class Submission(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    checked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="checked_submissions",
        null=True,
        blank=True,
    )
    answer = models.TextField()
    grade = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.student.groups.filter(name="Student").exists():
            raise ValidationError({
                "student": "Работу может сдавать только пользователь из группы Student."
            })

        if not CourseStudent.objects.filter(
            course=self.homework.course,
            student=self.student,
        ).exists():
            raise ValidationError({
                "student": "Этот ученик не записан на курс данной домашки."
            })

        if self.checked_by and not self.checked_by.groups.filter(name="Teacher").exists():
            raise ValidationError({
                "checked_by": "Проверяющий должен состоять в группе Teacher."
            })

        if self.checked_by and not HomeworkTeacher.objects.filter(
            homework=self.homework,
            teacher=self.checked_by,
        ).exists():
            raise ValidationError({
                "checked_by": "Этот преподаватель не назначен на данную домашку."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.homework.name}"

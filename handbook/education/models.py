from django.utils import timezone

from django.db import models
from django.utils.text import slugify
from accounts.models import User

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Course.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_course_slug")
        ]

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
    )
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"],
                name="unique_module_order_per_course",
            )
        ]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    slug = models.SlugField(blank=True, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Lesson.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "order"],
                name="unique_lesson_order_per_module",
            )
        ]

    def __str__(self):
        return self.title

class ContentBlock(models.Model):
    class BlockType(models.TextChoices):
        TEXT = "text"
        CODE = "code"
        NOTE = "note"
        IMAGE = "image"

    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="blocks"
    )

    type = models.CharField(max_length=20, choices=BlockType.choices)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        
        
class Task(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    starter_code = models.TextField(blank=True)
    slug = models.SlugField(blank=True, unique=True)
    order = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Task.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "order"],
                name="unique_task_order_per_lesson",
            )
        ]

    def __str__(self):
        return self.title

class SubmissionStatus(models.TextChoices):
    PENDING = "pending", "Проверка"
    DONE = "done", "Готово"
    FAILED = "failed", "Ошибка"

    
class Submission(models.Model):
    user = models.ForeignKey(
        User,
        related_name="submissions",
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        Task,
        related_name="submissions",
        on_delete=models.CASCADE
    )

    code = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.task}"


class ProgressStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", "В процессе"
    COMPLETED = "completed", "Завершено"
    
    
class UserProgress(models.Model):
    user = models.ForeignKey(
        User,
        related_name="progress",
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        Task,
        related_name="progress",
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=ProgressStatus.choices,
        default=ProgressStatus.IN_PROGRESS
    )

    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=["user", "task"],
                    name="unique_user_task_progress"
                )
            ]

    def save(self, *args, **kwargs):
        if self.status == ProgressStatus.COMPLETED:
            self.completed_at = self.completed_at or timezone.now()
        else:
            self.completed_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} → {self.task}"

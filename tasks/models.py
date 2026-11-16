from django.db import models


class Category(models.Model):
    """A group a task belongs to, e.g. Work, Study, Personal."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """A small label that can be attached to many tasks, e.g. urgent, home."""

    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    """The main model of the system."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # One category has many tasks (One-to-Many)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="tasks"
    )
    # A task can have many tags and a tag can be on many tasks (Many-to-Many)
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        # Duplicate prevention: same title cannot repeat inside one category
        constraints = [
            models.UniqueConstraint(
                fields=["title", "category"], name="unique_task_title_per_category"
            )
        ]

    def __str__(self):
        return self.title


class TaskDetail(models.Model):
    """Extra information for a task (One-to-One with Task)."""

    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name="detail"
    )
    additional_notes = models.TextField(blank=True)
    reminder_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Details of {self.task.title}"

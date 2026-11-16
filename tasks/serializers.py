from django.utils import timezone
from rest_framework import serializers

from .models import Category, Tag, Task, TaskDetail


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["created_at"]

    def validate_name(self, value):
        # Case-insensitive duplicate check ("Work" and "work" are the same)
        value = value.strip()
        queryset = Category.objects.filter(name__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "created_at"]
        read_only_fields = ["created_at"]

    def validate_name(self, value):
        value = value.strip()
        queryset = Tag.objects.filter(name__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A tag with this name already exists.")
        return value


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDetail
        fields = ["id", "task", "additional_notes", "reminder_date"]

    def validate_task(self, value):
        # Duplicate prevention: one task can have only one detail record
        queryset = TaskDetail.objects.filter(task=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("This task already has a detail record.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    # Read-only extras to make the response easier to read
    category_name = serializers.CharField(source="category.name", read_only=True)
    tag_names = serializers.SlugRelatedField(
        source="tags", many=True, read_only=True, slug_field="name"
    )
    # Nested detail (read only). Create/update it from /api/task-details/
    detail = TaskDetailSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_name",
            "tags",
            "tag_names",
            "status",
            "priority",
            "due_date",
            "detail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value

    def validate_due_date(self, value):
        # A new task cannot have a due date in the past
        if not self.instance and value < timezone.localdate():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate(self, data):
        # Duplicate prevention: same title cannot repeat in the same category
        title = data.get("title", getattr(self.instance, "title", None))
        category = data.get("category", getattr(self.instance, "category", None))
        queryset = Task.objects.filter(title__iexact=title, category=category)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "A task with this title already exists in this category."
            )
        return data

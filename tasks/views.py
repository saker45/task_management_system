from rest_framework import viewsets

from .filters import TaskFilter
from .models import Category, Tag, Task, TaskDetail
from .serializers import (
    CategorySerializer,
    TagSerializer,
    TaskDetailSerializer,
    TaskSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class TaskViewSet(viewsets.ModelViewSet):
    # select_related / prefetch_related reduce the number of database queries
    queryset = (
        Task.objects.select_related("category", "detail")
        .prefetch_related("tags")
        .all()
    )
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    search_fields = ["title", "description", "category__name", "tags__name"]
    ordering_fields = ["title", "due_date", "priority", "status", "created_at"]


class TaskDetailViewSet(viewsets.ModelViewSet):
    queryset = TaskDetail.objects.select_related("task").all()
    serializer_class = TaskDetailSerializer
    search_fields = ["additional_notes", "task__title"]
    ordering_fields = ["reminder_date"]

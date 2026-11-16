from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, TagViewSet, TaskDetailViewSet, TaskViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("tags", TagViewSet)
router.register("tasks", TaskViewSet)
router.register("task-details", TaskDetailViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

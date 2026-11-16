from django.contrib import admin

from .models import Category, Tag, Task, TaskDetail


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    ordering = ("name",)


class TaskDetailInline(admin.StackedInline):
    """Show the task detail on the same page as the task."""

    model = TaskDetail
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "priority", "due_date", "created_at")
    list_filter = ("status", "priority", "category", "due_date")
    search_fields = ("title", "description", "category__name", "tags__name")
    list_editable = ("status", "priority")
    filter_horizontal = ("tags",)
    date_hierarchy = "due_date"
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [TaskDetailInline]


@admin.register(TaskDetail)
class TaskDetailAdmin(admin.ModelAdmin):
    list_display = ("task", "reminder_date", "short_notes")
    search_fields = ("task__title", "additional_notes")
    list_filter = ("reminder_date",)

    @admin.display(description="Notes")
    def short_notes(self, obj):
        # Show only the first 50 characters in the list page
        return obj.additional_notes[:50]

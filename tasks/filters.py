import django_filters

from .models import Task


class TaskFilter(django_filters.FilterSet):
    # Date range filters: ?due_date_after=2026-01-01&due_date_before=2026-12-31
    due_date_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    # Filter by tag name: ?tag=urgent
    tag = django_filters.CharFilter(field_name="tags__name", lookup_expr="iexact")

    class Meta:
        model = Task
        fields = ["status", "priority", "category", "tag", "due_date_after", "due_date_before"]

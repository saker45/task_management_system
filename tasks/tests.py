from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Category, Tag, Task, TaskDetail


class TaskAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Study", description="University work")
        self.tag = Tag.objects.create(name="urgent")
        self.tomorrow = timezone.localdate() + timedelta(days=1)

    def make_task(self, title="Finish project", **extra):
        data = {
            "title": title,
            "category": self.category,
            "due_date": self.tomorrow,
        }
        data.update(extra)
        return Task.objects.create(**data)

    # ---------- Models ----------
    def test_str_methods(self):
        task = self.make_task()
        detail = TaskDetail.objects.create(task=task, additional_notes="Bring laptop")
        self.assertEqual(str(self.category), "Study")
        self.assertEqual(str(self.tag), "urgent")
        self.assertEqual(str(task), "Finish project")
        self.assertEqual(str(detail), "Details of Finish project")

    # ---------- CRUD ----------
    def test_create_task(self):
        payload = {
            "title": "Write report",
            "category": self.category.id,
            "tags": [self.tag.id],
            "priority": "high",
            "due_date": str(self.tomorrow),
        }
        response = self.client.post("/api/tasks/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["tag_names"], ["urgent"])
        self.assertEqual(response.data["status"], "pending")

    def test_retrieve_update_delete_task(self):
        task = self.make_task()
        url = f"/api/tasks/{task.id}/"
        self.assertEqual(self.client.get(url).status_code, 200)

        response = self.client.patch(url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "completed")

        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(Task.objects.filter(pk=task.id).exists())

    def test_category_and_tag_crud(self):
        response = self.client.post("/api/categories/", {"name": "Work"}, format="json")
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/tags/", {"name": "home"}, format="json")
        self.assertEqual(response.status_code, 201)

    def test_task_detail_create(self):
        task = self.make_task()
        payload = {"task": task.id, "additional_notes": "Check slides"}
        response = self.client.post("/api/task-details/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        # The nested detail now appears inside the task response
        response = self.client.get(f"/api/tasks/{task.id}/")
        self.assertEqual(response.data["detail"]["additional_notes"], "Check slides")

    # ---------- Validation & duplicates ----------
    def test_duplicate_category_name_rejected(self):
        response = self.client.post("/api/categories/", {"name": "study"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_duplicate_tag_name_rejected(self):
        response = self.client.post("/api/tags/", {"name": "URGENT"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_duplicate_task_in_same_category_rejected(self):
        self.make_task(title="Finish project")
        payload = {
            "title": "finish project",
            "category": self.category.id,
            "due_date": str(self.tomorrow),
        }
        response = self.client.post("/api/tasks/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_past_due_date_rejected(self):
        payload = {
            "title": "Old task",
            "category": self.category.id,
            "due_date": str(timezone.localdate() - timedelta(days=1)),
        }
        response = self.client.post("/api/tasks/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("due_date", response.data)

    def test_short_title_rejected(self):
        payload = {
            "title": "ab",
            "category": self.category.id,
            "due_date": str(self.tomorrow),
        }
        response = self.client.post("/api/tasks/", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)

    def test_second_detail_for_same_task_rejected(self):
        task = self.make_task()
        TaskDetail.objects.create(task=task)
        response = self.client.post("/api/task-details/", {"task": task.id}, format="json")
        self.assertEqual(response.status_code, 400)

    # ---------- Filtering, searching, ordering, pagination ----------
    def test_filter_by_status_and_priority(self):
        self.make_task(title="Task A", status="completed", priority="high")
        self.make_task(title="Task B", status="pending", priority="low")
        response = self.client.get("/api/tasks/?status=completed&priority=high")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Task A")

    def test_filter_by_tag(self):
        task = self.make_task(title="Tagged task")
        task.tags.add(self.tag)
        self.make_task(title="Plain task")
        response = self.client.get("/api/tasks/?tag=urgent")
        self.assertEqual(response.data["count"], 1)

    def test_search(self):
        self.make_task(title="Prepare viva slides")
        self.make_task(title="Buy groceries")
        response = self.client.get("/api/tasks/?search=viva")
        self.assertEqual(response.data["count"], 1)

    def test_ordering(self):
        self.make_task(title="Later task", due_date=self.tomorrow + timedelta(days=5))
        self.make_task(title="Sooner task")
        response = self.client.get("/api/tasks/?ordering=due_date")
        self.assertEqual(response.data["results"][0]["title"], "Sooner task")
        response = self.client.get("/api/tasks/?ordering=-due_date")
        self.assertEqual(response.data["results"][0]["title"], "Later task")

    def test_pagination(self):
        for i in range(7):
            self.make_task(title=f"Task number {i}")
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.data["count"], 7)
        self.assertEqual(len(response.data["results"]), 5)  # PAGE_SIZE = 5
        self.assertIsNotNone(response.data["next"])

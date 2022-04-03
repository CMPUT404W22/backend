import json
import uuid
from django.db import models
from author.models import Author


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, blank=False, null=False, on_delete=models.CASCADE)
    content = models.TextField(blank=False, null=False, default=False)  # must be json
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        data = json.loads(self.content)
        return str(data.get('summary', data.get("title", "comment")))

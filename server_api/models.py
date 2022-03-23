import uuid

from django.db import models

from author.models import Author


class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server_address = models.TextField(null=False)
    auth = models.TextField(null=False)

    class Meta:
        unique_together = ()

    def __str__(self):
        return f"Server: {self.server_address}"

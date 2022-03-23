import uuid

from django.db import models

from author.models import Author
from post.models import Post
from author.host import base_url


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, blank=False, null=False, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE)
    content = models.TextField(blank=False, null=False)
    type = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)

    def get_author(self):
        return Author.objects.get(id=self.author.id)

    def toJson(self):
        return {
            "type": "comment",
            "author": self.get_author().toJson(),
            "comment": self.content,
            "contentType": "text markdown",
            "published": self.updated,
            "id": f'{base_url}/authors/{self.author.id}/posts/{self.post.id}/comments/{self.id}',
        }




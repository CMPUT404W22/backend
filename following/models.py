from django.db import models
import uuid
from author.models import Author


class Following(models.Model):
    author = models.TextField(blank=False, null=False)
    following = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    objects = models.Manager()

    class Meta:
        unique_together = ('author', 'following',)

    def save(self, *args, **kwargs):
        if self.author != self.following:
            return super().save(*args, **kwargs)
        else:
            raise Exception("Authors cannot follow themselves")

    def get_author(self):
        return Author.objects.get(id=self.author)

    def __str__(self):
        return f"{self.author} is following ({self.following})"

class FollowRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, blank=False, null=False, on_delete=models.CASCADE, related_name='author')
    requesting_author = models.ForeignKey(Author, blank=False, null=False, on_delete=models.CASCADE, related_name='followerRequest')
    objects = models.Manager()

    class Meta:
        unique_together = ('author', 'requesting_author',)

    def save(self, *args, **kwargs):
        if self.author != self.requesting_author:
            return super().save(*args, **kwargs)
        else:
            raise Exception("Authors cannot send a follow request to themselves")

    def get_summary(self):
        return self.requesting_author.display_name + " wants to follow " + self.author.display_name

    def get_author(self):
        return Author.objects.get(id=self.author.id)

    def get_requesting_author(self):
        return Author.objects.get(id=self.requesting_author.id)

    def __str__(self):
        return f"FollowRequest id: {self.id}: user {self.requesting_author.id} wants to follow ({self.author.id})"

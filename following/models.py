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

    def get_summary(self):
        return f"{self.author} is following ({self.following})"

    def __str__(self):
        return f"{self.author} is following ({self.following})"

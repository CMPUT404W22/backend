import uuid

from django.db import models

from author.models import Author
from post.models import Post
from comment.models import Comment


class LikePost(models.Model):
    like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, blank=False, null=False, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE)
    summary = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ('author', 'post',)

    def get_author(self):
        return Author.objects.get(id=self.author.id)

    def __str__(self):
        return f"like_id {self.like_id}: author {self.author} liked ({self.post})"


class LikeComment(models.Model):
    like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, blank=False, null=False, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, blank=False, null=False, on_delete=models.CASCADE)
    summary = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ('author', 'comment',)

    def get_author(self):
        return Author.objects.get(id=self.author.id)

    def __str__(self):
        return f"like_id {self.like_id}: author {self.author} liked ({self.comment})"


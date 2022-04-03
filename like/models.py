import uuid

from django.db import models

from author.models import Author
from post.models import Post
from comment.models import Comment
from author import author_utility

class LikePost(models.Model):
    like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.TextField(blank=False, null=False)
    post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE)
    summary = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ('author', 'post',)

    def get_author(self):
        return author_utility.get_author(self.author)

    def get_author_id(self):
        return author_utility.get_author_id(self.author)

    def __str__(self):
        return f"like_id {self.like_id}: author {self.author} liked ({self.post})"


class LikeComment(models.Model):
    like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.TextField(blank=False, null=False)
    comment = models.ForeignKey(Comment, blank=False, null=False, on_delete=models.CASCADE)
    summary = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ('author', 'comment',)

    def get_author(self):
        return author_utility.get_author(self.author)

    def get_author_id(self):
        return author_utility.get_author_id(self.author)

    def __str__(self):
        return f"like_id {self.like_id}: author {self.author} liked ({self.comment})"


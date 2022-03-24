from rest_framework import serializers

from author.serializer import AuthorSerializer
from comment.models import Comment
from comment.serializer import CommentSerializer
from like.models import LikePost
from post.models import Post, Visibility, PostType
from author.host import base_url


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['type'] = "post"
        representation['title'] = instance.title
        representation['id'] = f'{base_url}/authors/{instance.author.id}/posts/{instance.id}'
        representation['description'] = instance.description
        representation['contentType'] = instance.type
        representation['content'] = instance.content
        representation['author'] = AuthorSerializer(instance.get_author(), many=False).data
        representation['categories'] = instance.categories
        representation['count'] = Comment.objects.filter(post=instance).count()
        representation['likeCount'] = LikePost.objects.filter(post=instance).count()
        representation['commentsSrc'] = CommentSerializer(Comment.objects.filter(post=instance), many=True).data
        representation['comments'] = f'{base_url}/authors/{instance.author.id}/posts/{instance.id}/comments'
        representation['published'] = instance.updated
        representation['visibility'] = instance.visibility
        representation['unlisted'] = instance.unlisted
        representation['image'] = instance.image

        return representation


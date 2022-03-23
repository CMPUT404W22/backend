from rest_framework import serializers

from author.serializer import AuthorSerializer
from comment.models import Comment
from post.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['type'] = "post"
        representation['title'] = instance.title
        representation['id'] = f'http://{base_url}:8000/authors/{instance.author.id}/posts/{instance.id}'
        representation['description'] = instance.description
        representation['contentType'] = instance.type
        representation['content'] = instance.content
        representation['author'] = AuthorSerializer(instance.get_author(), many=False).data
        representation['categories'] = instance.categories
        representation['count'] = Comment.objects.filter(post=instance).count()
        representation['comments'] = f'http://{base_url}:8000/authors/{instance.author.id}/posts/{instance.id}/comments'
        representation['published'] = instance.updated
        representation['visibility'] = instance.visibility
        representation['unlisted'] = instance.unlisted
        representation['image'] = instance.image

        return representation


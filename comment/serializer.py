from rest_framework import serializers

from author.serializer import AuthorSerializer
from comment.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['type'] = "comment"
        representation['author'] = AuthorSerializer(instance.get_author(), many=False).data
        representation['comment'] = instance.content
        representation['contentType'] = instance.type
        representation['published'] = instance.created
        representation['id'] = f"http://127.0.0.1:8000/authors/{instance.author.id}/posts/{instance.post.id}/comments/{instance.id}",

        return representation

from rest_framework import serializers

from author.serializer import AuthorSerializer
from comment.models import Comment
from author.host import base_url
from like.models import LikeComment


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
        representation['published'] = str(instance.created)
        representation['likeCount'] = LikeComment.objects.filter(comment=instance).count()
        representation['id'] = f"{base_url}/authors/{instance.get_author().id}/posts/{instance.post.id}/comments/{instance.id}"

        return representation

from rest_framework import serializers

from author.serializer import AuthorSerializer
from like.models import LikePost, LikeComment


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePost
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['type'] = "Like"
        representation['@context'] = "https://www.w3.org/ns/activitystreams"
        representation['summary'] = instance.summary
        representation['author'] = AuthorSerializer(instance.get_author(), many=False).data
        representation['object'] = f"http://127.0.0.1:8000/authors/{instance.author.id}/posts/{instance.post.id}"

        return representation


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeComment
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['type'] = "Like"
        representation['@context'] = "https://www.w3.org/ns/activitystreams"
        representation['summary'] = instance.summary
        representation['author'] = AuthorSerializer(instance.get_author(), many=False).data
        representation['object'] = f"http://127.0.0.1:8000/authors/{instance.author.id}/posts/{instance.comment.post.id}"

        return representation

from rest_framework import serializers

from author.author_utility import get_author_id
from author.serializer import AuthorSerializer
from like.models import LikePost, LikeComment
from author.host import base_url


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikePost
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['type'] = "Like"
        representation['@context'] = "https://www.w3.org/ns/activitystreams"
        representation['summary'] = instance.summary
        representation['author'] = instance.get_author()
        representation['object'] = f"{base_url}/authors/{instance.get_author_id()}/posts/{instance.post.id}"

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
        representation['author'] = instance.get_author()
        representation['object'] = f"{base_url}/authors/{instance.get_author_id()}/posts/{instance.comment.post.id}/comment/{instance.comment.id}"

        return representation

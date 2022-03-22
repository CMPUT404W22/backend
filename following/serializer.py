from rest_framework import serializers

from author.serializer import AuthorSerializer
from following.models import FollowRequest

class FollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowRequest
        fields = ()

    def to_representation(self, instance: FollowRequest):
        representation = super().to_representation(instance)
        representation["type"] = "Follow"
        representation["summary"] = instance.get_summary()
        representation["actor"] = AuthorSerializer(instance.get_requesting_author(), many=False).data
        representation["object"] = AuthorSerializer(instance.get_author(), many=False).data
        return representation

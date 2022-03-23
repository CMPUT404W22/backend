from rest_framework import serializers

from author.models import Author
from author.host import base_url


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['type'] = "author"
        representation['id'] = f"{base_url}/authors/{instance.id}"
        representation['url'] = f"{base_url}/authors/{instance.id}"
        representation['host'] = f"{base_url}/"
        representation['displayName'] = instance.display_name
        representation['github'] = instance.github
        representation['profileImage'] = instance.image

        return representation

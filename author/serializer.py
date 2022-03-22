from rest_framework import serializers

from author.models import Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['type'] = "author"
        representation['id'] = f"http://127.0.0.1:8000/authors/{instance.id}"
        representation['url'] = f"http://127.0.0.1:8000/authors/{instance.id}"
        representation['host'] = "http://127.0.0.1:8000/"
        representation['displayName'] = instance.display_name
        representation['github'] = instance.github
        representation['profileImage'] = instance.image

        return representation

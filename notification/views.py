from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework import response, status
from author.models import Author
from notification.models import Notification
from post.models import Post
from comment.models import Comment
from like.views import save_like_post, save_like_comment
import json

def parse_contents(author, data_json):
    # if contents is a LIKE, add to LikeComment/LikePost database
    # otherwise, return.
    if(data_json["type"] != "Like"):
        return

    summary: str = data_json["summary"]
    object_url = data_json["object"].split('/')
    last_index = len(object_url) - 1

    if('post' in summary.lower()):
        post = Post.objects.get(id=object_url[last_index])
        save_like_post(author, post)
    elif('comment' in summary.lower()):
        comment = Comment.objects.get(id=object_url[last_index])
        save_like_comment(author, comment)
    else:
        raise Exception(f"Invalid summary {summary}")

# Create your views here.
class NotificationsApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]

    def get(self, request, user_id):
        try:
            author = Author.objects.get(id=user_id)
            notifications = Notification.objects.filter(author=author)
            notifications.order_by('-created')

            items = []

            for n in notifications:
                items.append(n.content)

            result = {
                "type": "inbox",
                "items": [i for i in items]
            }
            return response.Response(result, status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Failed to get notifications: {e}", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, user_id):
        try:
            content = json.dumps(request.data)
            author = Author.objects.get(id=user_id)
            Notification.objects.create(author=author, content=content)
            parse_contents(author, request.data)
            return response.Response("Added notification", status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response(f"Failed to post to inbox: {e}", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        try:
            author = Author.objects.get(id=user_id)
            notifications = Notification.objects.filter(author=author)
            # delete all notifications
            for n in notifications:
                n.delete()
            return response.Response("Deleted", status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to delete: {e}", status=status.HTTP_400_BAD_REQUEST)

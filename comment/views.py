from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from rest_framework import response, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView

from author.models import Author
from comment.serializer import CommentSerializer
from post.models import Post
from comment.models import Comment
from author.host import base_url
from server_api.external import GetAllPostComments
from server_api.models import Server


class GetCommentsApiView(GenericAPIView):
    serializer_class = CommentSerializer
    authentication_classes = [BasicAuthentication, ]

    def get(self, request, user_id, post_id):
        if request.GET.get("origin") == "local":
            comments = Comment.objects.filter(post=post_id)

            if len(request.query_params) != 0:
                page = request.query_params["page"]
                size = 10
                try:
                    size = request.queryparams["size"]
                except Exception as _:
                    pass

                paginator = Paginator(comments, size)
                page_obj = paginator.get_page(page)

                result = {
                    "type": "comments",
                    "page": page,
                    "size": size,
                    "post": f'{base_url}/authors/{user_id}/posts/{post_id}/',
                    "id": f'{base_url}/authors/{user_id}/posts/{post_id}/comments',
                    "comments": self.serializer_class(page_obj, many=True).data

                }

                return response.Response(result, status=status.HTTP_200_OK)
            else:
                result = {
                    "type": "comments",
                    "post": f'{base_url}/authors/{user_id}/posts/{post_id}/',
                    "id": f'{base_url}/authors/{user_id}/posts/{post_id}/comments',
                    "comments": self.serializer_class(comments, many=True).data
                }

                return response.Response(result, status=status.HTTP_200_OK)
        else:
            server = Server.objects.get(server_address__icontains=f"{request.GET.get('origin')}")
            comments = GetAllPostComments(server, user_id, post_id)
            return response.Response(comments, status=status.HTTP_200_OK)

    def post(self, request, user_id, post_id):
        post = Post.objects.get(id=post_id)
        try:
            comment = Comment.objects.create(author=request.user, post=post)
            content = request.data["content"]

            comment.content = content
            comment.type = "text/plain"
            comment.save()

            result = self.serializer_class(comment, many=False)
            return response.Response(result.data, status=status.HTTP_201_CREATED)
        except Exception:
            return response.Response("Error", status=status.HTTP_400_BAD_REQUEST)


class CommentApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]

    def delete(self, request, user_id, post_id, comment_id):
        comment = Comment.objects.get(id=comment_id)
        if comment.author == request.user:
            comment.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
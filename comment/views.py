from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from rest_framework import response, status
from rest_framework.generics import GenericAPIView

from author.models import Author
from comment.serializer import CommentSerializer
from post.models import Post
from comment.models import Comment


class GetCommentsApiView(GenericAPIView):
    serializer_class = CommentSerializer

    def get(self, request, user_id, post_id):
        comments = Comment.objects.filter(author=user_id, post=post_id)

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
                "post": f'http://127.0.0.1:8000/authors/{user_id}/posts/{post_id}/',
                "id": f'http://127.0.0.1:8000/authors/{user_id}/posts/{post_id}/comments',
                "comments": self.serializer_class(page_obj, many=True).data

            }

            return response.Response(result, status=status.HTTP_200_OK)
        else:
            result = {
                "type": "comments",
                "post": f'http://127.0.0.1:8000/authors/{user_id}/posts/{post_id}/',
                "id": f'http://127.0.0.1:8000/authors/{user_id}/posts/{post_id}/comments',
                "comments": self.serializer_class(comments, many=True).data
            }

            return response.Response(result, status=status.HTTP_200_OK)

    def post(self, request, user_id, post_id):
        author = Author.objects.get(id=user_id)
        post = Post.objects.get(id=post_id)
        try:
            comment = Comment.objects.create(author=author, post=post)
            content = request.data["comment"]
            type = request.data["type"]

            comment.content = content
            comment.type = type
            comment.save()

            result = self.serializer_class(comment, many=False)
            return response.Response(result.data, status=status.HTTP_201_CREATED)
        except Exception:
            return response.Response("Error", status=status.HTTP_400_BAD_REQUEST)

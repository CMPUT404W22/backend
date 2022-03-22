from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework import response, status
from author.models import Author
from like.models import LikePost, LikeComment
from like.serializer import LikePostSerializer, LikeCommentSerializer
from post.models import Post
from comment.models import Comment

def save_like_post(author, post):
    like_post = LikePost.objects.create(author=author,post=post)
    like_post.author = author
    like_post.post = post
    like_post.summary = author.username + " Likes your post"
    like_post.save()


def save_like_comment(author, comment):
    like_comment = LikeComment.objects.create(author=author,comment=comment)
    like_comment.author = author
    like_comment.comment = comment
    like_comment.summary = author.username + " Liked on your comment"
    like_comment.save()

class GetLikeApiView(GenericAPIView):
    authentication_classes = []
    serializer_class = LikePostSerializer

    def get(self, request, user_id, post_id):
        # gets a list of likes from other authors on AUTHOR_ID’s post POST_ID
        try:
            post = Post.objects.get(id=post_id, author=user_id)
            likes = LikePost.objects.filter(post=post)
            return response.Response(self.serializer_class(likes, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error occurred: {e}", status.HTTP_404_NOT_FOUND)


class GetLikeCommentApiView(GenericAPIView):
    authentication_classes = []
    serializer_class = LikeCommentSerializer

    def get(self, request, user_id, post_id, comment_id):
        try:
            # post = Post.objects.get(id=post_id, author=user_id) # ensure that parameters passed are author's id, post id
            comment = Comment.objects.get(id=comment_id)
            likes = LikeComment.objects.filter(comment=comment)
            return response.Response(self.serializer_class(likes, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error occurred: {e}", status.HTTP_404_NOT_FOUND)


class GetLikedApiView(GenericAPIView):
    authentication_classes = []
    serializer_class_post = LikePostSerializer
    serializer_class_comment = LikeCommentSerializer

    def get(self, request, user_id):
        # gets posts and comment objects that the author likes
        try:
            author = Author.objects.get(id=user_id)
            liked_posts = LikePost.objects.filter(author=author)
            liked_comments = LikeComment.objects.filter(author=author)
            result = self.serializer_class_post(liked_posts, many=True).data + self.serializer_class_comment(
                liked_comments, many=True).data
            return response.Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error: {e}", status.HTTP_404_NOT_FOUND)

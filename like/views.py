# Create your views here.
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework import response, status
from author.models import Author
from like.models import LikePost, LikeComment
from like.serializer import LikePostSerializer, LikeCommentSerializer
from post.models import Post
from comment.models import Comment
from notification.models import Notification
from server_api.external import GetAllPostLikes, SendLike, GetAllCommentLikes, GetLiked
from server_api.models import Server
from author.serializer import AuthorSerializer


def save_like_post(author, post, name):
    like_post = LikePost.objects.create(author=author,post=post)
    like_post.author = author
    like_post.post = post
    like_post.summary = name + " likes your post"
    like_post.save()


def save_like_comment(author, comment, name):
    like_comment = LikeComment.objects.create(author=author,comment=comment)
    like_comment.author = author
    like_comment.comment = comment
    like_comment.summary = name + " liked on your comment"
    like_comment.save()


class GetLikeApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = LikePostSerializer

    def get(self, request, user_id, post_id):
        # gets a list of likes from other authors on AUTHOR_ID’s post POST_ID
        try:
            if request.GET.get("origin") == "local":
                post = Post.objects.get(id=post_id, author=user_id)
                likes = LikePost.objects.filter(post=post)
                return response.Response(self.serializer_class(likes, many=True).data, status=status.HTTP_200_OK)

            server = Server.objects.get(server_address__icontains=f"{request.GET.get('origin')}")
            likes = GetAllPostLikes(server, user_id, post_id)
            return response.Response(likes, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error occurred: {e}", status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id, post_id):
        if request.GET.get("origin") == "local":
            post = Post.objects.get(id=post_id)
            like = None
            try:
                like = LikePost.objects.create(author=request.user, post=post,
                                               summary=f"{request.user.display_name} likes your post")
                like.save()
                notification = Notification.objects.create(author=request.user, content=like)
                notification.save()
            except Exception as e:
                LikePost.objects.get(author=request.user, post=post).delete()
                return response.Response({"created": 0, "deleted": True}, status=status.HTTP_200_OK)

            return response.Response({"created": 1}, status=status.HTTP_201_CREATED)
        else:
            try:
                server = Server.objects.get(server_address__icontains=f"{request.GET.get('origin')}")
                author = AuthorSerializer(request.user, many=False).data
                code = SendLike(server, author, user_id, post_id)
                if code == 201:
                    return response.Response({"created": 1}, status=status.HTTP_200_OK)
                elif code == 200:
                    return response.Response({"created": 2}, status=status.HTTP_200_OK)
                else:
                    return response.Response({"created": 3}, status=status.HTTP_200_OK)

            except Exception as e:
                return response.Response({"created": 0}, status=status.HTTP_200_OK)


class GetLikeCommentApiView(GenericAPIView):
    authentication_classes = []
    serializer_class = LikeCommentSerializer

    def get(self, request, user_id, post_id, comment_id):
        try:
            if request.GET.get("origin") == "local":
                post = Post.objects.get(id=post_id, author=user_id) # ensure that parameters passed are author's id, post id
                comment = Comment.objects.get(id=comment_id, post=post)
                likes = LikeComment.objects.filter(comment=comment)
                return response.Response(self.serializer_class(likes, many=True).data, status=status.HTTP_200_OK)
            else:
                server = Server.objects.get(server_address__icontains=f"{request.GET.get('origin')}")
                likes = GetAllCommentLikes(server, user_id, post_id,comment_id)
                return response.Response(likes, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error occurred: {e}", status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id, post_id, comment_id):
        if request.GET.get("origin") == "local":
            comment = Comment.objects.get(id=comment_id)
            like = LikeComment.objects.create(author=request.user, comment=comment, summary=f"{request.user.display_name} liked your comment")
            like.save()
            return response.Response(self.serializer_class(like, many=False).data, status=status.HTTP_200_OK)
        else:
            return response.Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class GetLikedApiView(GenericAPIView):
    authentication_classes = []
    serializer_class_post = LikePostSerializer
    serializer_class_comment = LikeCommentSerializer

    def get(self, request, user_id):
        # gets posts and comment objects that the author likes
        try:
            if request.GET.get("origin") == "local":
                author = Author.objects.get(id=user_id)
                liked_posts = LikePost.objects.filter(author=author)
                liked_comments = LikeComment.objects.filter(author=author)
                result = self.serializer_class_post(liked_posts, many=True).data + self.serializer_class_comment(
                    liked_comments, many=True).data
                return response.Response(result, status=status.HTTP_200_OK)
            else:
                server = Server.objects.get(server_address__icontains=f"{request.GET.get('origin')}")
                likes = GetLiked(server, user_id)
                return response.Response(likes, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error: {e}", status.HTTP_404_NOT_FOUND)

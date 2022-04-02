from rest_framework import response, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView

from author.models import Author
from author.serializer import AuthorSerializer
from comment.models import Comment
from comment.serializer import CommentSerializer
from like.models import LikePost, LikeComment
from like.serializer import LikePostSerializer, LikeCommentSerializer
from notification.models import Notification
from post.models import Post
from post.serializer import PostSerializer
from author.host import base_url
from following.models import Following
from like.views import save_like_post, save_like_comment

import json

# region authors
class GetAuthorsApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def get(self, request):
        """
        Get Authors
        """
        users = Author.objects.all()

        result = {
            "type": "authors",
            "items": self.serializer_class(users, many=True).data
        }

        return response.Response(result, status=status.HTTP_200_OK)


class GetAuthorApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def get(self, request, id):
        """
        Get Author
        """
        user = Author.objects.get(id=id)
        result = self.serializer_class(user, many=False)
        return response.Response(result.data, status=status.HTTP_200_OK)
# endregion


# region followings
class GetFollowersApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def get(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            followers = [x.author for x in Following.objects.filter(following=author)]

            result = {
                "type": "followers",
                "items": AuthorSerializer(followers, many=True).data
            }
            return response.Response(result, status.HTTP_200_OK)

        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class CheckFollowersApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def get(self, request, author_id, follower_id):
        try:
            author = Author.objects.get(id=author_id)
            is_follower = Author.objects.get(id=follower_id)
            followers = Following.objects.filter(following=author)
            for follower in followers:
                if follower.author == is_follower:
                    return response.Response([self.serializer_class(is_follower, many=False).data], status.HTTP_200_OK)
            return response.Response([], status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to get followers: {e}", status=status.HTTP_400_BAD_REQUEST)
# endregion


# region posts
class GetPostsApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = PostSerializer

    def get(self, request, author_id):
        post = Post.objects.filter(author=author_id, visibility="Public")

        result = {
            "type": "posts",
            "items": self.serializer_class(post, many=True).data
        }

        return response.Response(result, status=status.HTTP_200_OK)


class GetPostApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = PostSerializer

    def get(self, request, author_id, post_id):
        try:
            post = Post.objects.get(id=post_id)
            result = self.serializer_class(post, many=False).data

            return response.Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(status=status.HTTP_404_NOT_FOUND)


class GetPostImageApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = PostSerializer

    def get(self, request, author_id, post_id):
        post = Post.objects.get(id=post_id)

        if post.type == "image/png;base64" or post.type == "image/jpeg;base64":
            return response.Response({"image": post.content}, status=status.HTTP_200_OK)
        else:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
# endregion


# region comments
class GetCommentsApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = CommentSerializer

    def get(self, request, author_id, post_id):
        comments = Comment.objects.filter(author=author_id, post=post_id)

        result = {
            "type": "comments",
            "post": f'{base_url}/authors/{author_id}/posts/{post_id}/',
            "id": f'{base_url}/authors/{author_id}/posts/{post_id}/comments',
            "comments": self.serializer_class(comments, many=True).data
        }

        return response.Response(result, status=status.HTTP_200_OK)
# endregion


# region likes
class GetLikeApiView(GenericAPIView):
    authentication_classes = []
    serializer_class = LikePostSerializer

    def get(self, request, author_id, post_id):
        # gets a list of likes from other authors on AUTHOR_ID’s post POST_ID
        try:
            post = Post.objects.get(id=post_id, author=author_id)
            likes = LikePost.objects.filter(post=post)
            return response.Response(self.serializer_class(likes, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error occurred: {e}", status.HTTP_404_NOT_FOUND)


class GetLikeCommentApiView(GenericAPIView):
    authentication_classes = []
    serializer_class = LikeCommentSerializer

    def get(self, request, author_id, post_id, comment_id):
        try:
            # post = Post.objects.get(id=post_id, author=user_id) # ensure that parameters passed are author's id, post id
            comment = Comment.objects.get(id=comment_id)
            likes = LikeComment.objects.filter(comment=comment)
            return response.Response(self.serializer_class(likes, many=True).data, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error occurred: {e}", status.HTTP_404_NOT_FOUND)

# endregion


# region liked
class GetLikedApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    serializer_class_post = LikePostSerializer
    serializer_class_comment = LikeCommentSerializer

    def get(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            liked_posts = LikePost.objects.filter(author=author)
            liked_comments = LikeComment.objects.filter(author=author)
            result = self.serializer_class_post(liked_posts, many=True).data + self.serializer_class_comment(
                liked_comments, many=True).data
            return response.Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(f"Error: {e}", status.HTTP_404_NOT_FOUND)
# endregion


# region inbox
def parse_contents(author, data_json):
    # if contents is a LIKE, add to LikeComment/LikePost database
    # otherwise, return.
    if(data_json["type"].lower() != "like"):
        return

    summary: str = data_json["summary"]
    object_url = data_json["object"].split('/')
    last_index = len(object_url) - 1

    if 'post' in summary.lower():
        post = Post.objects.get(id=object_url[last_index])
        save_like_post(author, post)
    elif 'comment' in summary.lower():
        comment = Comment.objects.get(id=object_url[last_index])
        save_like_comment(author, comment)
    else:
        raise Exception(f"Invalid summary {summary}")

class SendToInboxApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = None

    def post(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            content = json.dumps(request.data)
            Notification.objects.create(author=author, content=content)
            parse_contents(author, request.data)
            return response.Response("Notification Created", status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response(f"Failed to post to inbox: {e}", status=status.HTTP_400_BAD_REQUEST)
# endregion


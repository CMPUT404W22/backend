import base64

from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import response, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView


from author.models import Author
from following.models import Following
from post.serializer import PostSerializer
from post.models import Post, Visibility, PostType
import operator

from server_api.external import GetAllPost


class GetHomePagePosts(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = PostSerializer

    def get(self, request, user_id):
        request_type = request.GET.get('type')
        posts = None
        if request_type == "all":
            following = Following.objects.filter(author=request.user)
            posts = Post.objects.filter(author=request.user)

            for i in following:
                p = Post.objects.filter(Q(author=i.following) & Q(unlisted=False) & (Q(visibility=Visibility.PUBLIC) | Q(visibility=Visibility.FRIENDS)))
                posts = posts | p
        elif request_type == "self":
            posts = Post.objects.filter(author=request.user)
        elif request_type == "explore":
            authors = GetAllPost()
            return response.Response(authors, status=status.HTTP_200_OK)

        posts = reversed(sorted(posts, key=operator.attrgetter('created')))

        return response.Response(self.serializer_class(posts, many=True).data, status=status.HTTP_200_OK)


class GetPostsApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = PostSerializer

    def get(self, request, user_id):

        post = Post.objects.filter(author=user_id)

        if len(request.query_params) != 0:
            page = request.query_params["page"]
            size = 10
            try:
                size = request.queryparams["size"]
            except Exception as _:
                pass

            paginator = Paginator(post, size)
            page_obj = paginator.get_page(page)

            result = {
                "type": "posts",
                "items": self.serializer_class(page_obj, many=True).data
            }

            return response.Response(result, status=status.HTTP_200_OK)
        else:
            result = {
                "type": "posts",
                "items": self.serializer_class(post, many=True).data
            }

            return response.Response(result, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        author = Author.objects.get(id=user_id)
        try:
            post = Post.objects.create(author=author)
            title = request.data["title"]
            description = request.data["description"]
            content = request.data["content"]
            visibility = request.data["visibility"]
            categories = request.data["categories"]
            # count = request.data["count"]
            unlisted = request.data["unlisted"]
            image = request.data["image"]

            post.title = title
            post.description = description
            post.content = content
            post.visibility = visibility
            post.categories = categories
            post.unlisted = unlisted
            post.image = image
            post.save()

            result = self.serializer_class(post, many=False)
            return response.Response(result.data, status=status.HTTP_201_CREATED)
        except Exception:
            return response.Response("Error", status=status.HTTP_400_BAD_REQUEST)


class GetPostApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = PostSerializer

    def get(self, request, user_id, post_id):
        try:
            post = Post.objects.get(id=post_id)
            result = self.serializer_class(post, many=False).data

            return response.Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id, post_id):
        try:
            if str(request.user.id) == user_id:
                title = request.data["title"]
                description = request.data["description"]
                content = request.data["content"]
                visibility = request.data["visibility"]
                categories = request.data["categories"]
                unlisted = request.data["unlisted"]

                post = None
                try:
                    post = Post.objects.get(id=post_id)
                except:
                    post = Post.objects.create(id=post_id, author=request.user)
                post.title = title
                post.description = description
                post.content = content
                post.visibility = visibility
                post.categories = categories
                post.unlisted = unlisted
                post.type = "text/plain"
                post.save()

                result = self.serializer_class(post, many=False)
                return response.Response(result.data, status=status.HTTP_204_NO_CONTENT)
            else:
                return response.Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, post_id):
        try:
            post = Post.objects.get(id=post_id)
            post.delete()
            return response.Response("Deleted", status.HTTP_202_ACCEPTED)
        except Exception:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class GetPostImageApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = PostSerializer

    def get(self, request, author_id, post_id):
        post = Post.objects.get(id=post_id)

        if post.type == "image/png;base64" or post.type == "image/jpeg;base64":
            return response.Response({"image": post.content}, status=status.HTTP_200_OK)
        else:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
from rest_framework import response, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView
from author.models import Author
from author.serializer import AuthorSerializer
from following.models import Following, FollowRequest
from following.serializer import FollowRequestSerializer


class GetFollowersApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def get(self, request, user_id):
        # gets a list of authors who are user_id's followers
        try:
            author = Author.objects.get(id=user_id)
            followers = [x.author for x in Following.objects.filter(following=author)]

            result = {
                "type": "followers",
                "items": AuthorSerializer(followers, many=True).data
            }
            return response.Response(result, status.HTTP_200_OK)

        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class EditFollowersApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def delete(self, request, user_id, foreign_user_id):
        # remove FOREIGN_AUTHOR_ID as a follower of AUTHORs_ID
        try:
            follower = Author.objects.get(id=foreign_user_id)
            author = Author.objects.get(id=user_id)
            Following.objects.filter(author=follower, following=author).delete()
            return response.Response("Deleted", status.HTTP_202_ACCEPTED)
        except Exception as e:
            return response.Response(f"Error while trying to delete: {e}", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id, foreign_user_id):
        # Add FOREIGN_AUTHOR_ID as follower of AUTHOR_ID
        try:
            author = Author.objects.get(id=user_id)
            follower = Author.objects.get(id=foreign_user_id)
            Following.objects.create(author=follower, following=author)
            return response.Response("Added", status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response(f"Error while trying to add: {e}", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, user_id, foreign_user_id):
        # check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID
        try:
            author = Author.objects.get(id=user_id)
            is_follower = Author.objects.get(id=foreign_user_id)
            followers = Following.objects.filter(following=author)
            for follower in followers:
                if follower.author == is_follower:
                    return response.Response([self.serializer_class(is_follower, many=False).data], status.HTTP_200_OK)
            return response.Response([], status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to get followers: {e}", status=status.HTTP_400_BAD_REQUEST)


class FollowRequestApiView(GenericAPIView):
    def get(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            follow_requests = FollowRequest.objects.filter(author=author)
            items = []

            for fr in follow_requests:
                items.append(FollowRequestSerializer(fr))

            result = {
                "type": "follow requests",
                "items": [i.data for i in items]
            }
            return response.Response(result, status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to get list of follow requests: {e}", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, receiving_author_id, requesting_author_id):
        try:
            receiving_author = Author.objects.get(id=receiving_author_id)
            requesting_author = Author.objects.get(id=requesting_author_id)
            FollowRequest.objects.create(author=receiving_author, requesting_author=requesting_author)
            return response.Response("Follow request sent", status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response(f"Error while trying to add a follow request: {e}", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, receiving_author_id, requesting_author_id):
        try:
            receiving_author = Author.objects.get(id=receiving_author_id)
            requesting_author = Author.objects.get(id=requesting_author_id)
            FollowRequest.objects.filter(author=receiving_author, requesting_author=requesting_author).delete()
            return response.Response("Follow request successfully deleted", status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to delete follow request: {e}", status=status.HTTP_400_BAD_REQUEST)

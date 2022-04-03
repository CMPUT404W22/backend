from rest_framework import response, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView
from author.models import Author
from author.serializer import AuthorSerializer
from following.models import Following, FollowRequest
from following.serializer import FollowRequestSerializer
from server_api.models import Server
from server_api.external import GetAllFollowers, CheckFollower, delete_follower


class GetFollowersApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def get(self, request, user_id):
        # gets a list of authors who are user_id's followers
        try:
            address = request.GET.get("origin")
            if address == "local":
                author = Author.objects.get(id=user_id)
                author_serializer = self.serializer_class(author, many=False).data
                followers = [Author.objects.get(id = x.author.split('/')[-1]) for x in Following.objects.filter(following=author_serializer['id'])]
                result = {
                    "type": "followers",
                    "items": AuthorSerializer(followers, many=True).data
                }
                return response.Response(result, status.HTTP_200_OK)
            
            # remote
            server = Server.objects.get(server_address__icontains=f"{address}")
            followers = GetAllFollowers(server, user_id)
            return response.Response(followers, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class EditFollowersApiView(GenericAPIView):
    authentication_classes = [BasicAuthentication, ]
    serializer_class = AuthorSerializer

    def delete(self, request, user_id, foreign_user_id):
        # remove FOREIGN_AUTHOR_ID as a follower of AUTHORs_ID
        try:
            address = request.GET.get("origin")
            if address == "local":
                author = Author.objects.get(id=user_id)
                author_serializer = self.serializer_class(author, many=False).data
                follower = Author.objects.get(id=foreign_user_id)
                follower_serializer = self.serializer_class(follower, many=False).data
                Following.objects.filter(author=follower_serializer['id'], following=author_serializer['id']).delete()
                return response.Response("Deleted", status.HTTP_202_ACCEPTED)
            server = Server.objects.get(server_address__icontains=f"{address}")
            delete = delete_follower(server, user_id, foreign_user_id)
            return response.Response(delete, status.HTTP_202_ACCEPTED)
        except Exception as e:
            return response.Response(f"Error while trying to delete: {e}", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id, foreign_user_id):
        # Add FOREIGN_AUTHOR_ID as follower of AUTHOR_ID
        try:
            author = Author.objects.get(id=user_id)
            author_serializer = self.serializer_class(author, many=False).data
            follower = Author.objects.get(id=foreign_user_id)
            follower_serializer = self.serializer_class(follower, many=False).data
            Following.objects.create(author=follower_serializer['id'], following=author_serializer['id'])
            return response.Response("Added", status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response(f"Error while trying to add: {e}", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id, foreign_user_id):
        # check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID
        try:
            address = request.GET.get("origin")
            if address == "local":
                author = Author.objects.get(id=user_id)
                author_serializer = self.serializer_class(author, many=False).data
                is_follower = Author.objects.get(id=foreign_user_id)
                follower_serializer = self.serializer_class(is_follower, many=False).data
                followers = Following.objects.filter(following=author_serializer['id'])
                for follower in followers:
                    if follower.author == follower_serializer['id']:
                        return response.Response([follower_serializer], status.HTTP_200_OK)
                return response.Response([], status.HTTP_200_OK)

            server = Server.objects.get(server_address__icontains=f"{address}")
            follower = CheckFollower(server, user_id, foreign_user_id)
            if follower == "Not Found!" or follower == [] or follower == {} or follower == False:
                return response.Response([], status.HTTP_200_OK)
            return response.Response([follower], status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to get followers: {e}", status=status.HTTP_400_BAD_REQUEST)

class AllFollowRequestsApiView(GenericAPIView):
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

class FollowRequestApiView(GenericAPIView):
    def get(self, request, receiving_author_id, requesting_author_id):
        try:
            author = Author.objects.get(id=receiving_author_id)
            requesting_author = Author.objects.get(id=requesting_author_id)
            follow_requests = FollowRequest.objects.filter(author=author, requesting_author=requesting_author)
            
            if len(follow_requests) > 0:
                serialized_follow_request = FollowRequestSerializer(follow_requests[0]).data
                return response.Response([serialized_follow_request], status.HTTP_200_OK)
            return response.Response([], status.HTTP_200_OK)
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
            fr = FollowRequest.objects.filter(author=receiving_author, requesting_author=requesting_author)
            fr.delete()
            return response.Response("Follow request successfully deleted", status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to delete follow request: {e}", status=status.HTTP_400_BAD_REQUEST)

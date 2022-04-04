from rest_framework import response, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView
from author.models import Author
from author.serializer import AuthorSerializer
from following.models import Following
from server_api.models import Server
from server_api.external import GetAllFollowers, CheckFollower, delete_follower, GetAuthor
import json

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
                followers = Following.objects.filter(following=author_serializer['id'])

                items = []

                for f in followers:
                    id = f.author.split('/')[-1]
                    try:
                        follower = Author.objects.get(id)
                        i = AuthorSerializer(follower, many=False).data
                        items.append(i)
                    except Exception:
                        address = f.author.split('/')[2]
                        server = Server.objects.get(server_address__icontains=f"{address}")
                        i = GetAuthor(server, id)
                        items.append(i)

                result = {
                    "type": "followers",
                    "items": [i for i in items]
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

    def delete(self, request, user_id, foreign_user_id):
        # remove FOREIGN_AUTHOR_ID as a follower of AUTHORs_ID
        try:
            address = request.GET.get("origin")
            if address == "local":
                follower_id = request.data["actor"]["id"]
                following_id = request.data["object"]["id"]
                Following.objects.filter(author=follower_id, following=following_id).delete()
                return response.Response("Deleted", status.HTTP_202_ACCEPTED)
            server = Server.objects.get(server_address__icontains=f"{address}")
            delete = delete_follower(server, user_id, foreign_user_id)
            return response.Response(delete, status.HTTP_202_ACCEPTED)
        except Exception as e:
            return response.Response(f"Error while trying to delete: {e}", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id, foreign_user_id):
        # Add a follower using request data
        try:
            follower = request.data["actor"]["id"]
            following = request.data["object"]["id"]
            Following.objects.create(author=follower, following=following)
            return response.Response("Added", status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response(f"Error while trying to add: {e}", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id, foreign_user_id):
        # check if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID
        try:
            address = request.GET.get("origin")
            if address == "local":
                follower_id = request.GET.get("actor_id")
                following_id = request.GET.get("object_id")
                followers = Following.objects.filter(author=follower_id, following=following_id)
                if(len(followers) > 0):
                    return response.Response(True, status.HTTP_200_OK)
                return response.Response(False, status.HTTP_200_OK)

            server = Server.objects.get(server_address__icontains=f"{address}")
            follower = CheckFollower(server, user_id, foreign_user_id)
            if follower == "Not Found!" or follower == [] or follower == {} or follower == False:
                return response.Response(False, status.HTTP_200_OK)
            return response.Response(True, status.HTTP_200_OK)
        except Exception as e:
            return response.Response(f"Error while trying to get followers: {e}", status=status.HTTP_400_BAD_REQUEST)

from author.models import Author
from author.serializer import AuthorSerializer
from following.models import Following
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from server_api.models import Server
from unittest.mock import Mock, patch

class FollowersTestCase(APITestCase):
    # helper functions
    def addFollower(self, follower_serializer, following_serializer):
        Following.objects.create(author=follower_serializer["id"], following=following_serializer["id"])

    def checkFollower(self, follower_serializer, following_serializer):
        return Following.objects.filter(author=follower_serializer["id"], following=following_serializer["id"])

    def setUp(self):
        # create server
        self.server: Server = Server.objects.create(server_address="https://cmput404-w22-project-backend.herokuapp.com/", auth="username:password")

        # create users
        Author.objects.create_user(username="test1", password="password",
                                   display_name="test1", github="0")

        Author.objects.create_user(username="user1", password="password",
                                   display_name="user1", github="1")

        Author.objects.create_user(username="user2", password="password",
                                   display_name="user2", github="2")

        # get the ids of the users
        self.author1: Author = Author.objects.get(username="user1")
        self.author1_id = self.author1.id
        self.author1_serializer = AuthorSerializer(self.author1, many=False).data

        self.author2: Author = Author.objects.get(username="user2")
        self.author2_id = self.author2.id
        self.author2_serializer = AuthorSerializer(self.author2, many=False).data

        self.user = Author.objects.get(username="test1")
        self.id = self.user.id

        # Authenticate user
        self.client = APIClient()
        self.client.login(username='test1', password='password')

        self.mock_remote_follower_response = {"type": "followers"}
        self.mock_remote_author = {
            "type":"author",
            "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
            "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
            "host":"http://127.0.0.1:5454/",
            "displayName":"Greg Johnson",
            "github": "http://github.com/gjohnson",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        }

    # GetFollowersApiView region
    def test_get_followers_local_empty(self):
        # it should return an empty list if there are no followers
        response = self.client.get(f'/service/authors/{self.author1_id}/followers?origin=local')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"type":"followers","items":[]}')


    def test_get_followers_local(self):
        # it should have a list of followers in response["items"] if we add a follower
        self.addFollower(self.author2_serializer, self.author1_serializer)

        response = self.client.get(f'/service/authors/{self.author1_id}/followers?origin=local')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data["items"]), 1)

    # mock out call to GetAllFollowers()
    @patch('following.views.GetAllFollowers')
    def test_get_followers_remote(self, getAllFollowers_mock: Mock):
        # it should return response from GetAllFollowers()
        getAllFollowers_mock.return_value = self.mock_remote_follower_response
        response = self.client.get(f'/service/authors/{self.author1_id}/followers?origin={self.server.server_address}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data, self.mock_remote_follower_response)

    def test_get_followers_fail(self):
        # it should fail if we send a bad request
        invalidId = "123"
        response = self.client.get(f'/service/authors/{invalidId}/followers?origin={self.server.server_address}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    # endof GetFollowersApiView region

    # GetFriendsApiView region
    @patch('following.views.GetAuthor')
    def test_has_friends(self, getAuthor_mock: Mock):
        # it should return a list of friends if there's bidirectional following
        getAuthor_mock.return_value = self.mock_remote_author
        self.addFollower(self.author1_serializer, self.author2_serializer)
        self.addFollower(self.author2_serializer, self.author1_serializer)

        response = self.client.get(f'/service/authors/{self.author1_id}/friends')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["items"]), 1)

    def test_no_friends(self):
        # it should return an empty list if there's no bidirectional following
        response = self.client.get(f'/service/authors/{self.author1_id}/friends')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"type":"friends","items":[]}')

    def test_get_friend_fail(self):
        # it should fail if we send a bad request
        invalidId = "123"
        response = self.client.get(f'/service/authors/{invalidId}/friends')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    # endof GetFriendsApiView region

    # EditFollowersApiView region
    def test_delete_followers_local(self):
        # it should delete local follower
        self.addFollower(self.author2_serializer, self.author1_serializer)

        following = { "object": self.author1_serializer["id"]}

        response = self.client.delete(f'/service/authors/{self.author2_id}/followers/{self.author1_id}?origin=local',
            following,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.content, b'"Deleted"')

        # check that it was deleted from database
        result = self.checkFollower(self.author2_serializer, self.author1_serializer)
        self.assertEqual(len(result), 0)

    @patch('following.views.delete_follower')
    def test_delete_followers_remote(self, delete_follower_mock: Mock):
        # it should delete local follower
        delete_follower_mock.return_value = "Deleted"
        self.addFollower(self.author2_serializer, self.author1_serializer)

        response = self.client.delete(f'/service/authors/{self.author1_id}/followers/{self.author2_id}?origin={self.server.server_address}')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.content, b'"Deleted"')

    def test_invalid_delete(self):
        # it should fail if invalid id is sent
        invalid_id = "123"
        response = self.client.delete(f'/service/authors/{self.id}/followers/{invalid_id}?origin=local')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_follower(self):
        # it should add a new follower
        follower = {"actor": self.author2_serializer}
        response = self.client.put(f'/service/authors/{self.author1_id}/followers/{self.author2_id}',
            follower,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)    

        # check if db was updated
        result = self.checkFollower(self.author2_serializer, self.author1_serializer)
        self.assertEqual(len(result), 1)

    def test_invalid_put(self):
        # it should return 400 error if author id is invalid
        invalid_id = "123"
        response = self.client.put(f'/service/authors/{self.author1_id}/followers/{invalid_id}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)    

    def test_check_follower_local_false(self):
        # it should return false if author2 is not following author1
        response = self.client.get(f'/service/authors/{self.author1_id}/followers/{self.author2_id}?origin=local&actor_id={self.author2_serializer["id"]}&object_id={self.author1_serializer["id"]}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'false')

    def test_check_follower_local_true(self):
        # it should return true if author2 is following author1
        self.addFollower(self.author2_serializer, self.author1_serializer)

        response = self.client.get(f'/service/authors/{self.author1_id}/followers/{self.author2_id}?origin=local&actor_id={self.author2_serializer["id"]}&object_id={self.author1_serializer["id"]}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'true')

    @patch('following.views.CheckFollower')
    def test_check_follower_remote(self, checkFollower_mock: Mock):
        # it should return false if author2 is not following author1
        checkFollower_mock.return_value = True
        response = self.client.get(f'/service/authors/{self.author1_id}/followers/{self.author2_id}?origin={self.server.server_address}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'true')
    # endof EditFollowersApiView region

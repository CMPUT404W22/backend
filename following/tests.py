from author.models import Author
from following.models import FollowRequest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

class FollowersTestCase(APITestCase):
    def setUp(self):
        # create users
        Author.objects.create_user(username="test1", password="password",
                                   display_name="test1", github="0")

        Author.objects.create_user(username="user1", password="password",
                                   display_name="user1", github="1")

        Author.objects.create_user(username="user2", password="password",
                                   display_name="user2", github="2")

        # get the ids of the users
        self.author1 = Author.objects.get(username="user1")
        self.foreign_id1 = self.author1.id

        self.author2 = Author.objects.get(username="user2")
        self.foreign_id2 = self.author2.id

        self.user = Author.objects.get(username="test1")
        self.id = self.user.id

        # Authenticate user
        self.client = APIClient()
        self.client.login(username='test1', password='password')

    def test_get_followers(self):
        # testing get before adding any followers
        response = self.client.get(f'/service/authors/{self.id}/followers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"type":"followers","items":[]}')

    def test_put_and_delete_followers(self):
        # testing adding a follower
        response = self.client.put(f'/service/authors/{self.id}/followers/{self.foreign_id1}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.content, b'"Added"')

        # check that it was added to the database
        response = self.client.get(f'/service/authors/{self.id}/followers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.content, b'{"type":"followers","items":[]}')

        # test delete
        response = self.client.delete(f'/service/authors/{self.id}/followers/{self.foreign_id1}')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.content, b'"Deleted"')

        # check that it was removed from the database
        response = self.client.get(f'/service/authors/{self.id}/followers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"type":"followers","items":[]}')

    def test_get_is_follower(self):
        # check when is a follower
        self.client.put(f'/service/authors/{self.id}/followers/{self.foreign_id2}')
        response = self.client.get(f'/service/authors/{self.id}/followers/{self.foreign_id2}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'"True"')

    def test_get_not_follower(self):
        # check when not a follower
        response = self.client.get(f'/service/authors/{self.id}/followers/{self.foreign_id1}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'"False"')

    def test_invalid_delete(self):
        # test when trying to delete follower that is not in database
        invalid_id = "123"
        response = self.client.delete(f'/service/authors/{self.id}/followers/{invalid_id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_put(self):
        # test when trying to delete follower that is not in database
        invalid_id = "123"
        response = self.client.put(f'/service/authors/{self.id}/followers/{invalid_id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_get(self):
        # test when uses an id that is not valid
        invalid_id = "123"
        response = self.client.delete(f'/service/authors/{self.id}/followers/{invalid_id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class FollowRequestTestCase(APITestCase):
    def setUp(self):
        # create users
        Author.objects.create_user(username="user1", password="password",
                                   display_name="user1", github="1")

        Author.objects.create_user(username="user2", password="password",
                                   display_name="user2", github="2")

        # get the ids of the users
        self.author1: Author = Author.objects.get(username="user1")
        self.author_id_1 = self.author1.id

        self.author2: Author = Author.objects.get(username="user2")
        self.author_id_2 = self.author2.id

        # Authenticate
        self.client = APIClient()
        self.client.login(username='user1', password='password')

    def test_get_empty(self):
        # it should get a 200 OK response
        response = self.client.get(f'/service/authors/{self.author_id_1}/followerRequests')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"type":"follow requests","items":[]}')

    def test_get_contents(self):
        # add data to DB
        # it should get a 200 OK response
        FollowRequest.objects.create(author=self.author1, requesting_author=self.author2)
        response = self.client.get(f'/service/authors/{self.author_id_1}/followerRequests')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['items']), 1)

    def test_invalid_get(self):
        # it should send 400 BAD REQUEST response if author id is invalid
        invalid_id = 123
        response = self.client.get(f'/service/authors/{invalid_id}/followerRequests')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post(self):
        # it should create new database entry and send 200 OK response
        response = self.client.post(f'/service/authors/{self.author_id_1}/followerRequests/{self.author_id_2}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.content, b'"Follow request sent"')

    def test_fail_post(self):
        # it should fail if author id is invalid and send 400 BAD REQUEST
        invalid_id = 123
        response = self.client.post(f'/service/authors/{invalid_id}/followerRequests/{self.author_id_2}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        # it should delete database entry and send 200 OK response
        FollowRequest.objects.create(author=self.author1, requesting_author=self.author2)
        response = self.client.delete(f'/service/authors/{self.author_id_1}/followerRequests/{self.author_id_2}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'"Follow request successfully deleted"')

    def test_fail_delete(self):
        # it should fail if author id is invalid and send 400 BAD REQUEST
        invalid_id = 123
        response = self.client.delete(f'/service/authors/{invalid_id}/followerRequests/{self.author_id_2}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

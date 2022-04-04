from author.models import Author
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

    # GetFriendsApiView region
    def test_get_followers(self):
        # testing get before adding any followers
        response = self.client.get(f'/service/authors/{self.id}/followers')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"type":"followers","items":[]}')
    # endof GetFriendsApiView region

    # EditFollowersApiView region
    # endof EditFollowersApiView region
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
        self.assertIn(b'"type":"author"', response.content)

    def test_get_not_follower(self):
        # check when not a follower
        response = self.client.get(f'/service/authors/{self.id}/followers/{self.foreign_id1}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'[]')

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

from author.models import Author
from notification.models import Notification
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# Create your tests here.
class NotificationTestCase(APITestCase):
    def setUp(self):
        # create users
        Author.objects.create_user(username="user1", password="password",
                                   display_name="user1", github="1")

        # get the ids of the users
        self.author: Author = Author.objects.get(username="user1")
        self.author_id = self.author.id

        self.request = {"type": "Post"}

        # Authenticate
        self.client = APIClient()
        self.client.login(username='user1', password='password')

    def test_get_empty(self):
        # it should return 200 OK response and empty items list
        response = self.client.get(f'/service/authors/{self.author_id}/inbox')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"type":"inbox","items":[]}')

    def test_get_contents(self):
        # add to DB
        # it should return 200 OK response and contents
        Notification.objects.create(author=self.author, content="some content here")
        response = self.client.get(f'/service/authors/{self.author_id}/inbox')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['items']), 1)

    def test_fail_get(self):
        # it should return  400 BAD REQUEST response if given invalid author id
        invalid_id = '123'
        response = self.client.get(f'/service/authors/{invalid_id}/inbox')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post(self):
        # it should add notification and return 201 CREATED response
        response = self.client.post(f'/service/authors/{self.author_id}/inbox', self.request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.content, b'"Added notification"')
        notifications = Notification.objects.filter(author=self.author)
        self.assertEqual(len(notifications), 1)

    def test_fail_post(self):
        # it should return  400 BAD REQUEST response if given invalid author id
        invalid_id = '123'
        response = self.client.post(f'/service/authors/{invalid_id}/inbox', self.request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        # it should delete everything from the Notification table and return 200 OK
        Notification.objects.create(author=self.author, content="some content")
        response = self.client.delete(f'/service/authors/{self.author_id}/inbox')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'"Deleted"')
        items = Notification.objects.filter(author=self.author)
        self.assertEqual(len(items), 0)

    def test_fail_delete(self):
        invalid_id = '123'
        response = self.client.delete(f'/service/authors/{invalid_id}/inbox')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

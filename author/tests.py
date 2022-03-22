from author.models import Author
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
import uuid

class AuthorTestCase(APITestCase):

    def setUp(self):
        # create users
        self.author = Author.objects.create(
            id = uuid.uuid4(),
            username = "user",
            display_name = "display Name",
            github = "github0"
        )
        
        self.id = self.author.id
        
        self.post_author = {
            "displayName" : "user1",
            "github" : "3",
            "profileImage" : "image"
        }
        
        # Authenticate user
        self.client = APIClient()
        self.client.login(username='user', password='pswd')
        
    def test_get_author(self):
        response = self.client.get(f'/service/authors/{self.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.author.id, self.id)
        self.assertEqual(self.author.display_name, "display Name")
        self.assertEqual(self.author.github, "github0")
        
    # def test_post_author(self):
    #     request = self.post_author
    #     self.client.post("/login/", {"username":"user","password":"pswd"})
    #     response = self.client.post(f'/service/authors/{self.id}/', request)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
  
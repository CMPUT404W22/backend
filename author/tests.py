from re import S
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
        
    
        self.user = {
            "username":"user2",
            "password":"password",
            "display_name":"uuuuser",
            "github":"github1"
        }
        
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
        
    def test_post_and_put_author(self):
        # test post a author
        request = self.user
        response = self.client.post(f"/admin/login/", request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        
        # test put method
        response = self.client.put(f'/service/authors/{id}/', self.post_author)
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)
        
    def fail_post_and_put_author(self):
        # test post a author
        user = Author.objects.create(
            password = "password33",
            display_name = "uuuuser", 
            github = "github1"
        )
        request = self.user
        response = self.client.post(f"/admin/login/", request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        
    def test_invalid_get(self):
        # test when uses an id that is not valid
        invalidId = "123"
        response = self.client.get(f'/service/authors/{invalidId}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def unauthorized_author(self):
        # the users has authorized yet
        response = self.client.post(f'/service/authors/', self.post_author)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        

    
    
        
        
        
        
  
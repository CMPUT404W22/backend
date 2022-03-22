from post.models import Post
from author.models import Author
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status



class FollowersTestCase(APITestCase):

    def setUp(self):
        # create users
        Author.objects.create_user(username="test1", password="password",
                                   display_name="test1", github="0")
        
        Author.objects.create_user(username="user1", password="password",
                                   display_name="user1", github="1")

        # get the ids of the users
        self.user = Author.objects.get(username="test1")
        self.id = self.user.id
        
        self.author1 = Author.objects.get(username="user1")
        self.foreignId1 = self.author1.id
        
        # create a post 
        self.post = Post.objects.create(
            id=self.id, 
            author = self.user,
            type = 0,
            title = "TheTitle",
            description = "TheDescription",
            content = "Nice Day!",
            visibility = 0,
            unlisted = False,
            categories = "Nice"
        )
        # image post
        self.Image_Post = {
            "id" : self.id,
            "author" : self.id,
            "type" : 3,
            "title" : "ImgTitle",
            "description" : "ImgDescription",
            "content" : "Nice Image!",
            "visibility" : 0,
            "unlisted" : False,
            "image" : "Here is image",
            "categories" : "Img"
        }

        # Authenticate user
        self.client = APIClient()
        self.client.login(username='test1', password='password')

    def test_get_post(self):
        # test getting posts
        response = self.client.get(f'/service/authors/{self.id}/posts/{self.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post.id, self.id)
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.type, 0)
        self.assertEqual(self.post.title, "TheTitle")
        self.assertEqual(self.post.description, "TheDescription")
        self.assertEqual(self.post.content, "Nice Day!")
        self.assertEqual(self.post.visibility, 0)
        self.assertEqual(self.post.unlisted, False)
        self.assertEqual(self.post.categories, "Nice")

    def test_post_post(self):
        request = self.Image_Post
        response = self.client.post(f'/service/authors/{self.id}/posts/', request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_posts(self):
        # test deleting a post
        response = self.client.delete(f'/service/authors/{self.id}/posts/{self.id}')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.content, b'"Deleted"')
        
    def test_invalid_delete(self):
        # test when trying to delete follower that isnt in database
        response = self.client.delete(f'/service/authors/{self.id}/posts/{self.foreignId1}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_get(self):
        # test when uses an id that is not valid
        invalidId = "123"
        response = self.client.delete(f'/service/authors/{self.id}/posts/{invalidId}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_invalid_post(self):
        Invalid_Post = {
            "id" : "33333",
            "author" : "3333333",
            "type" : "2333",
            "title" : "ImgTitle",
            "description" : "ImgDescription",
            "content" : "Nice Image!",
            "visibility" : "not",
            "unlisted" : False,
            "image" : "Here is image",
            "categories" : "Img"
        }
        response = self.client.post(f'/service/authors/{self.foreignId1}/posts/', Invalid_Post)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

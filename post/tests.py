from unicodedata import category
from post.models import Post, Visibility
from author.models import Author
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status



class PostTestCase(APITestCase):

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
        
        self.author2 = Author.objects.get(username="user1")
        self.foreignId2 = self.author2.id
        
        # create a post 
        self.post1 = Post.objects.create(
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
        
        self.post2 = Post.objects.create(
            id = self.foreignId1,
            author = self.author1,
            type = 0,
            title = "Title",
            description = "Description",
            content = "Content",
            visibility = 1,
            unlisted = False,
            categories = "Cate"
        )
        
        # set a image post
        self.post_image_id ="2566778"
        self.Image_Post = {
            "id" : self.post_image_id,
            "author" : self.user,
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
        self.client.login(username='user1', passowrd='password')

    def test_get_posts(self):
        # test getting posts
        response1 = self.client.get(f'/service/authors/{self.id}/posts/{self.id}')
        response2 = self.client.get(f'/service/authors/{self.foreignId1}/posts/{self.foreignId1}')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        # if self.post1 works, then self.post2 works in the same way
        self.assertEqual(self.post1.id, self.id)
        self.assertEqual(self.post1.author, self.user)
        self.assertEqual(self.post1.type, 0)
        self.assertEqual(self.post1.title, "TheTitle")
        self.assertEqual(self.post1.description, "TheDescription")
        self.assertEqual(self.post1.content, "Nice Day!")
        self.assertEqual(self.post1.visibility, 0)
        self.assertEqual(self.post1.unlisted, False)
        self.assertEqual(self.post1.categories, "Nice")

    def test_post_post(self):
        request = self.Image_Post
        response = self.client.post(f'/service/authors/{self.id}/posts/', request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        

    def test_delete_posts(self):
        # test deleting a post
        response = self.client.delete(f'/service/authors/{self.id}/posts/{self.id}')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.content, b'"Deleted"')
        
    def test_invalid_post_post(self):
        # test when tring to post a post to a invalid author
        request = self.Image_Post
        invalidId = "45673952"
        response = self.client.post(f'/service/authors/{invalidId}/posts/', request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_invalid_delete(self):
        # test when trying to delete follower that isnt in database
        invalidId = "45673952"
        response = self.client.delete(f'/service/authors/{self.id}/posts/{invalidId}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_get(self):
        # test when uses an id that is not valid
        invalidId = "123"
        response = self.client.delete(f'/service/authors/{self.id}/posts/{invalidId}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

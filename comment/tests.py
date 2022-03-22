from post.models import Post
from comment.models import Comment
from author.models import Author
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase


class CommentTestCase(APITestCase):

    def setUp(self):
        # create users
        Author.objects.create_user(username="test1", password="password",
                                   display_name="test1", github="0")

        # get the ids of the users
        self.user = Author.objects.get(username="test1")
        self.id = self.user.id
        
        #create a post first
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
        
        # create a comment
        self.comment = Comment.objects.create(
            id = self.id,
            author = self.user,
            post = self.post,
            content = "Good Comment",
            type = "comment"
            )
        
        self.post_comment = {
            "comment" : "Post Comment",
            "type" : "comment"
        }

        # Authenticate user
        self.client = APIClient()
        self.client.login(username='test1', password='password')

    def test_get_comment(self):
        response = self.client.get(f'/service/authors/{self.id}/posts/{self.id}/comments')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.comment.id, self.id)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.content, "Good Comment")
        self.assertEqual(self.comment.type, "comment")
        
        
    def test_post_comment(self):
        request = self.post_comment
        response = self.client.post(f'/service/authors/{self.id}/posts/{self.id}/comments', request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_invalid_post_comment(self):
        request = self.post_comment
        response = self.client.post(f'/service/authors/{self.id}/posts/',request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
        
        
from post.models import Post
from comment.models import Comment
from author.models import Author
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from author.host import base_url
from server_api.models import Server
from unittest.mock import Mock, patch

class CommentTestCase(APITestCase):

    def setUp(self):
        # create server
        self.server: Server = Server.objects.create(server_address="remote_address", auth="username:password")

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

        self.comment_request_response = {
            "type": "comment",
            "content" : "new comment added",
        }

        # Authenticate user
        self.client = APIClient()
        self.client.login(username='test1', password='password')

    def test_get_comment_local_no_other_query_params(self):
        # it should return result from the
        # origin == local && len(request.GET) <= 1 block
        response = self.client.get(f'/service/authors/{self.id}/posts/{self.id}/comments?origin=local')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        comment_item_0 = response_data["comments"][0]

        self.assertEqual(response_data["type"], "comments")
        self.assertEqual(response_data["post"], f'{base_url}/authors/{self.id}/posts/{self.id}/')
        self.assertEqual(response_data["id"], f'{base_url}/authors/{self.id}/posts/{self.id}/comments')
        self.assertEqual(comment_item_0["comment"], self.comment.content)

        # "page" and "size" should not exist
        with self.assertRaises(KeyError):
            response_data["page"]
        with self.assertRaises(KeyError):
            response_data["size"]

    def test_get_comment_local_with_query_params(self):
        # it should return result from the
        # origin == local && len(request.GET) > 1 block
        page = 6
        size = 9

        response = self.client.get(f'/service/authors/{self.id}/posts/{self.id}/comments?origin=local&page={page}&size={size}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        comment_item_0 = response_data["comments"][0]

        self.assertEqual(response_data["type"], "comments")
        self.assertEqual(response_data["page"], f'{page}')
        self.assertEqual(response_data["size"], f'{size}')
        self.assertEqual(response_data["post"], f'{base_url}/authors/{self.id}/posts/{self.id}/')
        self.assertEqual(response_data["id"], f'{base_url}/authors/{self.id}/posts/{self.id}/comments')
        self.assertEqual(comment_item_0["comment"], self.comment.content)

    # mock out call to GetAllPostComments()
    @patch('comment.views.GetAllPostComments')
    def test_get_comment_server(self, getAllPostComments_mock: Mock):
        # it should return comments from server and call server_api's GetAllPostComments() function correctly
        # origin != local

        getAllPostComments_mock.return_value = self.comment_request_response

        response = self.client.get(f'/service/authors/{self.id}/posts/{self.id}/comments?origin={self.server.server_address}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        getAllPostComments_mock.assert_called_once()
        getAllPostComments_mock.assert_called_with(self.server, f'{self.id}', f'{self.id}')
        self.assertEqual(response.data, self.comment_request_response)

    def test_get_comment_invalid_origin(self):
        # it should FAIL if origin is not specified
        response = self.client.get(f'/service/authors/{self.id}/posts/{self.id}/comments')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_post_comment(self):
        # it should add a new comment to a post
        response = self.client.post(f'/service/authors/{self.id}/posts/{self.post.id}/comments', self.comment_request_response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_invalid_post_comment_content(self):
        # it should fail if there's no "content" key in request data
        response = self.client.post(f'/service/authors/{self.id}/posts/{self.post.id}/comments', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_comment_invalid_post_id(self):
        # it should fail if post id does not exist
        invalid_id = '123'
        response = self.client.post(f'/service/authors/{self.id}/posts/{invalid_id}/comments', self.comment_request_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.urls import path

from server_api import views

urlpatterns = [
    path('authors/', views.GetAuthorsApiView.as_view(), name="Get Authors"),
    path('authors/<str:id>', views.GetAuthorApiView.as_view(), name="Get Authors"),
    path('authors/<str:author_id>/followers', views.GetFollowersApiView.as_view(), name="Get Followers"),
    path('authors/<str:author_id>/followers/<str:follower_id>', views.CheckFollowersApiView.as_view(), name="Get Follower"),
    path('authors/<str:author_id>/posts/', views.GetPostsApiView.as_view(), name="Get Posts"),
    path('authors/<str:author_id>/posts/<str:post_id>', views.GetPostApiView.as_view(), name="Get Post"),
    path('authors/<str:author_id>/posts/<str:post_id>/image', views.GetPostImageApiView.as_view(), name="Get Post Image"),
    path('authors/<str:author_id>/posts/<str:post_id>/comments', views.GetCommentsApiView.as_view(), name="Get Post Image"),
    path('authors/<str:author_id>/posts/<str:post_id>/likes', views.GetLikeApiView.as_view(), name="send like"),
    path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes', views.GetLikeCommentApiView.as_view(), name="liked comments"),
    path('authors/<str:author_id>/liked', views.GetLikedApiView.as_view(), name="liked"),
    path('authors/<str:author_id>/inbox', views.SendToInboxApiView.as_view(), name="Send to inbox "),
]

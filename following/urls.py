from django.urls import path
from following import views as followingViews

urlpatterns = [
    path('<str:user_id>/followers', followingViews.GetFollowersApiView.as_view(), name="get follower"),
    path('<str:user_id>/friends', followingViews.GetFriendsApiView.as_view(), name="get friends"),
    path('<str:user_id>/followers/<str:foreign_user_id>', followingViews.EditFollowersApiView.as_view(), name="edit follower"),
]

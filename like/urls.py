from django.urls import path
from like import views

urlpatterns = [
    path('<str:user_id>/posts/<str:post_id>/likes', views.GetLikeApiView.as_view(), name="send like"),
    path('<str:user_id>/posts/<str:post_id>/comments/<str:comment_id>/likes', views.GetLikeCommentApiView.as_view(), name="liked comments"),
]

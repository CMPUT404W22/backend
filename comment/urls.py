from django.urls import path
from comment import views

urlpatterns = [
    path('', views.GetCommentsApiView.as_view(), name="comments"),
    path('<str:comment_id>', views.CommentApiView.as_view(), name="comment"),
]

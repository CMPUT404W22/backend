from django.urls import path

from author import views
from like import views as likesViews

urlpatterns = [
    path('', views.GetAuthorsApiView.as_view(), name="authors"),
    path('login/', views.Login.as_view(), name="login"),
    path('<str:user_id>/', views.GetAuthorApiView.as_view(), name="author"),
    path('<str:user_id>/liked', likesViews.GetLikedApiView.as_view(), name="liked"),
]

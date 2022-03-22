from django.urls import path
from notification import views as notificationViews

urlpatterns = [
    path('<str:user_id>/inbox', notificationViews.NotificationsApiView.as_view(), name = "notifications in inbox")
]

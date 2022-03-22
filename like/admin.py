from django.contrib import admin

from like.models import LikePost, LikeComment

admin.site.register(LikePost)
admin.site.register(LikeComment)

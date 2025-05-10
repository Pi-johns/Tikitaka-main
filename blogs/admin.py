# blog/admin.py

from django.contrib import admin
from .models import Blog, Comment, CommentLike

admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(CommentLike)

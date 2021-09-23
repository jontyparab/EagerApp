from django.contrib import admin
from .models import Category, Post, Collection, Vote, Comment, VoteComment, FileRef

# Register your models here.
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Collection)
admin.site.register(Vote)
admin.site.register(Comment)
admin.site.register(VoteComment)
admin.site.register(FileRef)

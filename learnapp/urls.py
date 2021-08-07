from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # Posts
    path('post/list/', PostListView.as_view(), name='post_list'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/detail/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),


    # Collections
    path('collection/list/', CollectionListView.as_view(), name='collection_list'),
    path('collection/create/', CollectionCreateView.as_view(), name='collection_create'),
    path('collection/<int:pk>/detail/', CollectionDetailView.as_view(), name='collection_detail'),
    path('collection/<int:pk>/update/', CollectionUpdateView.as_view(), name='collection_update'),
    path('collection/<int:pk>/delete/', CollectionDeleteView.as_view(), name='collection_delete'),

    # Vote
    path('vote/create/', VoteCreateView.as_view(), name='vote_create'),
    # path('vote/<int:pk>/update/', VoteUpdateView.as_view(), name='vote_update'),  # pk = Post.id
    # path('vote/<int:pk>/delete/', VoteDeleteView.as_view(), name='vote_delete'),  # pk = Post.id
    path('vote/<int:pk>/detail/', VoteRetrieveUpdateDestroyView.as_view(), name='vote_rud'),  # pk = Post.id

    # Category
    path('category/list', CategoryListView.as_view(), name='category_list'),
]

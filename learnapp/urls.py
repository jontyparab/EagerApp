from django.contrib import admin
from django.conf import settings
from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    # Posts
    path('post/list/', PostListView.as_view(), name='post_list'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/detail/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),

    # Vote Post
    path('vote/create/', VoteCreateView.as_view(), name='vote_create'),
    path('vote/<int:pk>/detail/', VoteRetrieveUpdateDestroyView.as_view(), name='vote_detail'),  # pk = Post.id

    # Collections
    path('collection/list/', CollectionListView.as_view(), name='collection_list'),
    path('collection/create/', CollectionCreateView.as_view(), name='collection_create'),
    path('collection/<int:pk>/detail/', CollectionDetailView.as_view(), name='collection_detail'),
    path('collection/<int:pk>/update/', CollectionUpdateView.as_view(), name='collection_update'),
    path('collection/<int:pk>/delete/', CollectionDeleteView.as_view(), name='collection_delete'),

    # Comments
    path('comment/<int:pk>/list/', CommentListView.as_view(), name='comment_list'),  # pk = Post.id
    path('comment/create/', CommentCreateView.as_view(), name='comment_create'),
    # path('comment/<int:pk>/detail/', CommentDetailView.as_view(), name='comment_detail'), // Not needed
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),

    # Vote Comment
    path('vote_comment/create/', VoteCommentCreateView.as_view(), name='vote_create'),
    path('vote_comment/<int:pk>/detail/', VoteCommentRetrieveUpdateDestroyView.as_view(), name='vote_comment_rud'),  # pk = Comment.id

    # Category
    path('category/list', CategoryListView.as_view(), name='category_list'),

    # File Upload
    path('file/', FileStorageView.as_view(), name='upload_image_view')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

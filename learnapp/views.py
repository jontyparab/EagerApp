import re
from django.conf import settings
from decouple import config

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from rest_framework import status
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView, RetrieveAPIView, \
    RetrieveUpdateDestroyAPIView
import pyrebase
import os

from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.db.models import Avg, Count, Sum
from django.contrib.auth import get_user_model
from .serializers import PostSerializer, CollectionSerializer, VoteSerializer, CategorySerializer, CommentSerializer, \
    VoteCommentSerializer
from accounts.models import UserProfile
from .models import Post, Collection, Vote, Category, Comment, VoteComment, FileRef


# POSTS
class PostCreateView(CreateAPIView):
    # authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    model = Post
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        return serializer.save(author=self.request.user)


class PostDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Post
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class PostUpdateView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Post
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'], author=self.request.user)
        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        obj = self.get_object()
        serializer.is_valid(raise_exception=True)
        if obj.author == self.request.user:
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied(detail='Permission denied.')


class PostDeleteView(DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Post
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'], author=self.request.user)
        return obj

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            super(PostDeleteView, self).perform_destroy(instance)
        else:
            raise PermissionDenied(detail='Permission denied.')


class PostListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Post
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = self.filter_helper()
        return queryset

    def filter_helper(self):
        search = [x.lower() for x in self.request.query_params.getlist('search')]
        username = self.request.query_params.get('username')
        query = self.request.query_params.get("query")
        category = self.request.user.userprofile.category.values_list('id', flat=True)
        print("WHOA", search, type(username), type(category))
        if username:
            if search:
                print('username search ran')
                # Only shows posts that have all fields matching
                queryset = Post.objects.filter(author__username=username, tags__contains=search)
            else:
                print('only username ran')
                queryset = Post.objects.filter(author__username=username)
        elif search:
            print('only search ran')
            queryset = Post.objects.filter(category__in=category, tags__contains=search)
            print(queryset, category)
        else:
            print('else ran')
            queryset = Post.objects.filter(category__in=category)

        if query == "newest":
            queryset = queryset.order_by('-created')
        elif query == "rating":
            queryset = sorted(queryset, key=lambda a: a.score, reverse=True)
        else:
            queryset = queryset
        return queryset


# POST VOTES
class VoteCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Vote
    serializer_class = VoteSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        return serializer.save(voter=self.request.user)


class VoteRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Vote
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, post__id=self.kwargs['pk'], voter=self.request.user)
        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        obj = self.get_object()
        serializer.is_valid(raise_exception=True)
        if obj.voter == self.request.user:
            serializer.save(voter=self.request.user)
        else:
            raise PermissionDenied(detail='Permission denied.')

    def perform_destroy(self, instance):
        if instance.voter == self.request.user:
            super(VoteRetrieveUpdateDestroyView, self).perform_destroy(instance)
        else:
            raise PermissionDenied(detail='Permission denied.')


# COLLECTIONS
class CollectionCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Collection
    serializer_class = CollectionSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        return serializer.save(author=self.request.user)


class CollectionDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Collection
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'], author=self.request.user)
        return obj


class CollectionUpdateView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Collection
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'], author=self.request.user)
        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        obj = self.get_object()
        serializer.is_valid(raise_exception=True)
        if obj.author == self.request.user:
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied(detail='Permission denied.')


class CollectionDeleteView(DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Collection
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'], author=self.request.user)
        return obj

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            super(CollectionDeleteView, self).perform_destroy(instance)
        else:
            raise PermissionDenied(detail='Permission denied.')


class CollectionListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Collection
    serializer_class = CollectionSerializer

    def get_queryset(self):
        queryset = Collection.objects.filter(author=self.request.user)
        return queryset


# COMMENTS
class CommentCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Comment
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        return serializer.save(author=self.request.user)


# class CommentDetailView(RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     model = Comment
#     serializer_class = CommentSerializer
#     queryset = Comment.objects.all()


class CommentDeleteView(DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Comment
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, post__id=self.kwargs['pk'], author=self.request.user)
        return obj

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            super(CommentDeleteView, self).perform_destroy(instance)
        else:
            raise PermissionDenied(detail='Permission denied.')


class CommentListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Comment
    serializer_class = CommentSerializer

    def get_queryset(self):
        if Post.objects.filter(id=self.kwargs['pk']).exists():
            queryset = Comment.objects.filter(post__id=self.kwargs['pk'])
            queryset = sorted(queryset, key=lambda a: a.score, reverse=True)
        else:
            raise NotFound(detail='The post with given id doesn\'t exist')
        return queryset


# COMMENT VOTE
class VoteCommentCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = VoteComment
    serializer_class = VoteCommentSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        return serializer.save(voter=self.request.user)


class VoteCommentRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = VoteComment
    serializer_class = VoteCommentSerializer
    queryset = VoteComment.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, comment__id=self.kwargs['pk'], voter=self.request.user)
        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        obj = self.get_object()
        serializer.is_valid(raise_exception=True)
        if obj.voter == self.request.user:
            serializer.save(voter=self.request.user)
        else:
            raise PermissionDenied(detail='Permission denied.')

    def perform_destroy(self, instance):
        if instance.voter == self.request.user:
            super(VoteCommentRetrieveUpdateDestroyView, self).perform_destroy(instance)
        else:
            raise PermissionDenied(detail='Permission denied.')


# class VoteUpdateView(UpdateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     model = Vote
#     serializer_class = VoteSerializer
#     queryset = Vote.objects.all()
#
#     def get_object(self):
#         queryset = self.get_queryset()
#         obj = get_object_or_404(queryset, post__id=self.kwargs['pk'], voter=self.request.user)
#         return obj
#
#     def partial_update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return self.update(request, *args, **kwargs)
#
#     def perform_update(self, serializer):
#         obj = self.get_object()
#         serializer.is_valid(raise_exception=True)
#         if obj.voter == self.request.user:
#             serializer.save(voter=self.request.user)
#         else:
#             raise PermissionDenied(detail='Permission denied.')
#
#
# class VoteDeleteView(DestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     model = Vote
#     serializer_class = VoteSerializer
#     queryset = Vote.objects.all()
#
#     def get_object(self):
#         queryset = self.get_queryset()
#         obj = get_object_or_404(queryset, post__id=self.kwargs['pk'], voter=self.request.user)
#         return obj
#
#     def perform_destroy(self, instance):
#         if instance.voter == self.request.user:
#             super(VoteDeleteView, self).perform_destroy(instance)
#         else:
#             raise PermissionDenied(detail='Permission denied.')


# CATEGORY
class CategoryListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Category
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


# STORAGE
# Configuration
config = {
    "apiKey": config('fire_apiKey'),
    "authDomain": config('fire_authDomain'),
    "projectId": config('fire_projectId'),
    "storageBucket": config('fire_storageBucket'),
    "messagingSenderId": config('fire_messagingSenderId'),
    "appId": config('fire_appId'),
    "databaseURL": config('fire_databaseURL'),
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
db = firebase.database()

# For Service Account (pyrebase bug)
config['serviceAccount'] = os.path.join(settings.BASE_DIR, 'google-credentials.json')
firebase_super = pyrebase.initialize_app(config)
storage_super = firebase_super.storage()


class FileStorageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            # Getting image
            file = request.FILES["image"]
            # print(f"=======================", os.path.join(settings.BASE_DIR, 'firebase-credentials.json'))
            if bool(re.match('image/', file.content_type)) and file.size < 3000000:
                file_key = db.generate_key()  # generating unique key
                default_storage.save(file_key, file)  # Temporarily storing it in default storage

                # Saving to firebase storage
                uploadedImage = storage.child(f"images/{file_key}").put(f"media/{file_key}")
                # print('=======', uploadedImage)
                uploadedImageURL = storage.child(f"images/{file_key}").get_url(uploadedImage['downloadTokens'])
                default_storage.delete(file_key)  # deleting from temporary storage

                # Create a entry in FileRef for later reference
                FileRef.objects.create(author=request.user, name=uploadedImage['name'], url=uploadedImageURL)

                return Response({
                    "status": True,
                    "url": uploadedImageURL
                }, status=status.HTTP_201_CREATED)
            else:
                print('=============', bool(re.match('image/', file.content_type)), file.size < 3000000)
                raise ValueError('File should be image and less than 5MB.')
        except Exception:
            raise ValidationError(detail="Failed to upload file.")

    def delete(self, request):
        file_url = request.data['url']
        print('===============', file_url)
        bucket = storage_super.bucket
        file_ref = FileRef.objects.get(url=file_url)
        if file_ref.author == request.user:
            blob = bucket.blob(file_ref.name)
            blob.delete()
            file_ref.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(detail='Something went wrong')

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView, RetrieveAPIView, \
    RetrieveUpdateDestroyAPIView
from django.db import IntegrityError
from django.db.models import Avg, Count, Sum
from django.contrib.auth import get_user_model
from .serializers import PostSerializer, CollectionSerializer, VoteSerializer, CategorySerializer, CommentSerializer, \
    VoteCommentSerializer
from accounts.models import UserProfile
from .models import Post, Collection, Vote, Category, Comment, VoteComment


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

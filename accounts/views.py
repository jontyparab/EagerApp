from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListCreateAPIView, DestroyAPIView, RetrieveUpdateAPIView, \
    RetrieveUpdateDestroyAPIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserProfileSerializer
from .models import UserProfile

UserModel = get_user_model()


class UserCreateView(CreateAPIView):
    model = UserModel
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        UserProfile.objects.create(user=user)


class UserListView(ListCreateAPIView):
    model = UserModel
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()


class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    model = UserModel
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.request.user.id)
        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        obj = self.get_object()
        serializer.is_valid(raise_exception=True)
        if obj == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied(detail='Permission denied.')

    def perform_destroy(self, instance):
        if instance == self.request.user:
            super(UserRetrieveUpdateDestroyView, self).perform_destroy(instance)
        else:
            raise PermissionDenied(detail='Permission denied.')


# class UserDestroyView(DestroyAPIView):
#     model = UserModel
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = UserSerializer
#     queryset = UserModel.objects.all()
#
#     def get_object(self):
#         queryset = self.get_queryset()
#         obj = get_object_or_404(queryset, id=self.request.user.id)
#         return obj
#
#     def perform_destroy(self, instance):
#         if instance == self.request.user:
#             super(UserDestroyView, self).perform_destroy(instance)
#         else:
#             raise PermissionDenied(detail='Permission denied.')


class UserProfileUpdateView(RetrieveUpdateAPIView):
    model = UserProfile
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        obj = self.get_object()
        serializer.is_valid(raise_exception=True)
        if obj.user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied(detail='Permission denied.')

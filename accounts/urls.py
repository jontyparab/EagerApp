from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', UserCreateView.as_view(), name='user_create'),
    path('list/', UserListView.as_view(), name='user_list'),
    # path('delete/', UserDestroyView.as_view(), name='user_delete'),
    path('', UserRetrieveUpdateDestroyView.as_view(), name='user_delete'),
    path('profile/', UserProfileUpdateView.as_view(), name='user_profile_update'),
]

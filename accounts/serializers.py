from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from .models import UserProfile
from learnapp.serializers import CategorySerializer, PostSerializer
from learnapp.validators import username_validator

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    read_only_fields = ('id',)

    def validate_username(self, value):
        if username_validator(value):
            raise ValidationError('Please enter valid username.')
        return value

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # response['profile'] = UserProfileSerializer(instance.userprofile).data
        return response

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'].lower(),
            password=validated_data['password'],
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email).lower()
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'email', 'password')


class UserProfileSerializer(serializers.ModelSerializer):
    # category = CategorySerializer(many=True)
    # saved_posts = PostSerializer(many=True)

    def validate(self, attrs):
        save_type = self.context['request'].data.get('type', None) in ['post_add', 'post_remove']
        # If update with posts then type field is necessary
        if self.instance:
            if 'saved_posts' in attrs and not save_type:
                raise ValidationError("Field 'type' necessary to save posts.")
        return attrs

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        response['category'] = CategorySerializer(instance.category, many=True).data
        response['saved_posts'] = PostSerializer(instance.saved_posts, many=True).data
        return response

    def update(self, instance, validated_data):
        save_type = self.context['request'].data.get('type')
        category = validated_data.get('category')
        saved_posts = validated_data.get('saved_posts')

        if save_type == 'post_remove' and saved_posts:
            instance.saved_posts.remove(*validated_data.get('saved_posts'))
            # Remove removed post from all collections as well
            for collection in instance.user.collection_set.all():
                collection.posts.remove(*validated_data.get('saved_posts'))
        elif save_type == 'post_add' and saved_posts:
            instance.saved_posts.add(*validated_data.get('saved_posts'))

        if category:
            instance.category.clear()
            instance.category.add(*validated_data.get('category', instance.category.all()))
        instance.save()
        return instance

    class Meta:
        model = UserProfile
        fields = ('user', 'category', 'saved_posts')

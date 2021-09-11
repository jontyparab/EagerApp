from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from .models import Post, Collection, Vote, Category, Comment, VoteComment
from .validators import tag_validator
from django.db.models import ObjectDoesNotExist, Avg, Count, Sum
import time

UserModel = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response

    class Meta:
        model = Category
        fields = ('id', 'name')


class PostSerializer(serializers.ModelSerializer):
    score = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField(source='author.username')
    resources = serializers.ListField(child=serializers.URLField())
    tags = serializers.ListField(child=serializers.CharField())
    # category = CategorySerializer
    read_only_fields = ('id', 'score', 'author')

    def validate_tags(self, value):
        unique_tags = list(set(value))
        for tag in unique_tags:
            tag_validator(tag)
        # for tag in unique_tags:
        #     if tag_validator(tag):
        #         raise ValidationError('Please enter valid tags.')
        return unique_tags

    def validate(self, attrs):
        author = self.context['request'].user
        title = attrs.get('title')

        # User can't have a post with the same title twice...
        try:
            check_post = Post.objects.get(author=author, title=title)
        except ObjectDoesNotExist:
            check_post = None

        if not self.instance:
            if check_post:
                raise serializers.ValidationError('You have already made a post with this title.')
            else:
                return attrs
        elif self.instance:
            if (not check_post) or (check_post == self.instance):
                return attrs
            else:
                raise serializers.ValidationError('You have already made a post with this title.')
        else:
            raise serializers.ValidationError('Something went wrong...')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['category'] = CategorySerializer(instance.category).data.get('name')
        return response

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.resources = validated_data.get('resources', instance.resources)
        instance.category = validated_data.get('category', instance.category)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.save()
        return instance

    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'description', 'resources', 'tags', 'category', 'score')


class VoteSerializer(serializers.ModelSerializer):
    voter = serializers.ReadOnlyField(source='voter.username')

    # Can be used when fields are included in Meta fields
    # validators = [
    #     UniqueTogetherValidator(
    #         queryset=Vote.objects.all(),
    #         fields=['voter', 'post'],
    #         message='Something went wrong...',
    #     ),
    # ]

    def validate(self, attrs):
        voter = self.context['request'].user
        post = attrs.get('post')
        if not self.instance:
            if Vote.objects.filter(voter=voter, post=post).exists():
                raise serializers.ValidationError('Already voted.')
            else:
                return attrs
        elif self.instance:
            return attrs
        else:
            raise serializers.ValidationError('Something went wrong...')

    def update(self, instance, validated_data):
        instance.vote = validated_data.get('vote', instance.vote)
        instance.save()
        return instance

    class Meta:
        model = Vote
        fields = ('voter', 'post', 'vote')


class CollectionSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    # posts = PostSerializer(many=True)
    read_only_fields = ('id', 'author')

    def validate_posts(self, value):
        user = self.context['request'].user
        # Might not be efficient
        # for post in value:
        #     if not user.userprofile.saved_posts.filter(id=post.id).exists():
        #         raise ValidationError('Only saved posts can be added or removed from collections.')
        saved_set = set(list(user.userprofile.saved_posts.filter(id__in=[x.id for x in value])))
        to_save_set = set(value)
        if not to_save_set.issubset(saved_set):
            raise ValidationError('Only saved posts can be added or removed from collections.')
        return value

    def validate(self, attrs):
        save_type = self.context['request'].data.get('type', None) in ['post_add', 'post_remove']
        # if update with posts then type field is necessary
        if self.instance:
            if 'posts' in self.context['request'].data and not save_type:
                raise ValidationError("Field 'type' necessary to save posts.")

        author = self.context['request'].user
        title = attrs.get('title')
        # User can't have a collection with the same title twice...
        try:
            check_collection = Collection.objects.get(author=author, title=title)
        except ObjectDoesNotExist:
            check_collection = None

        if not self.instance:
            if check_collection:
                raise serializers.ValidationError('You have already made a collection with this title.')
            else:
                return attrs
        elif self.instance:
            if (not check_collection) or (check_collection == self.instance):
                return attrs
            else:
                raise serializers.ValidationError('You have already made a collection with this title.')
        else:
            raise serializers.ValidationError('Something went wrong...')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['posts'] = PostSerializer(instance.posts, many=True).data
        return response

    def update(self, instance, validated_data):
        save_type = self.context['request'].data.get('type')
        posts = validated_data.get('posts')

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        if save_type == 'post_remove' and posts:
            instance.posts.remove(*validated_data.get('posts'))
        elif save_type == 'post_add' and posts:
            instance.posts.add(*validated_data.get('posts'))

        # new_posts = set(validated_data.get('posts', instance.posts))
        # old_posts = set(instance.posts.all())
        # req_posts = new_posts.symmetric_difference(old_posts)
        # for post in req_posts:
        #     if post in new_posts:
        #         pass
        #         instance.posts.add(post)
        #     else:
        #         pass
        #         instance.posts.remove(post)
        instance.save()
        return instance

    class Meta:
        model = Collection
        fields = ('id', 'author', 'title', 'description', 'posts')


class CommentSerializer(serializers.ModelSerializer):
    score = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField(source='author.username')
    read_only_fields = ('id', 'score', 'author')
    
    def validate(self, attrs):
        author = self.context['request'].user
        post = attrs.get('post')

        # User can't comment on a post twice...
        try:
            check_comment = Comment.objects.get(author=author, post=post)
        except ObjectDoesNotExist:
            check_comment = None

        # self.instance is only present while updating method
        if not self.instance:
            if check_comment:
                raise serializers.ValidationError('You have already commented on this post.')
            else:
                return attrs
        elif self.instance:
            if (not check_comment) or (check_comment == self.instance):
                return attrs
            else:
                raise serializers.ValidationError('You have already commented on this post.')
        else:
            raise serializers.ValidationError('Something went wrong...')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response

    def update(self, instance, validated_data):
        instance.post = validated_data.get('post', instance.description)
        instance.body = validated_data.get('body', instance.resources)
        instance.save()
        return instance

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'body', 'score')


class VoteCommentSerializer(serializers.ModelSerializer):
    voter = serializers.ReadOnlyField(source='voter.username')

    def validate(self, attrs):
        voter = self.context['request'].user
        comment = attrs.get('comment')
        if not self.instance:
            if VoteComment.objects.filter(voter=voter, comment=comment).exists():
                raise serializers.ValidationError('Already voted this comment.')
            else:
                return attrs
        elif self.instance:
            return attrs
        else:
            raise serializers.ValidationError('Something went wrong...')

    def update(self, instance, validated_data):
        instance.vote = validated_data.get('vote', instance.vote)
        instance.save()
        return instance

    class Meta:
        model = VoteComment
        fields = ('voter', 'comment', 'vote')

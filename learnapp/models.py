from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db.models import Avg, Count, Sum
from django.utils.translation import gettext_lazy as _
from .validators import tag_validator

UserModal = get_user_model()


# algorithms = 'Algorithms'
# ai = "AI"
# testing = 'Testing'
# os = 'Operating System'
# programming = 'Programming'
# se = 'Software Engineering'
# networking = 'Networking'
# hardware = 'Hardware'


class FileRef(models.Model):
    author = models.ForeignKey(UserModal, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    url = models.URLField()

    def __str__(self):
        return f"#{self.id} {self.name} {self.url}"


class Category(models.Model):
    name = models.CharField(max_length=254)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"#{self.id} {self.name}"


class Post(models.Model):
    author = models.ForeignKey(UserModal, on_delete=models.CASCADE)
    title = models.CharField(max_length=254, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    resources = ArrayField(models.URLField(blank=True), size=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = ArrayField(models.CharField(max_length=30, validators=[tag_validator]), size=10, null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def score(self):
        score = self.vote_set.aggregate(sum=Sum('vote'))['sum']
        return score or 0

    def __str__(self):
        return f"#{self.id} {self.title} - by {self.author}"


class Collection(models.Model):
    author = models.ForeignKey(UserModal, on_delete=models.CASCADE)
    title = models.CharField(max_length=254, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    posts = models.ManyToManyField(Post, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"#{self.id} {self.title} Collection - by {self.author}"


class Vote(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'post'], name='unique_vote'),
        ]

    class VoteType(models.IntegerChoices):
        downvote = -1, _("Down Vote")
        upvote = 1, _("Up Vote")

    voter = models.ForeignKey(UserModal, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote = models.IntegerField(choices=VoteType.choices)

    def __str__(self):
        return f"#{self.id} {self.voter} voted {self.post.title}"


class Comment(models.Model):
    author = models.ForeignKey(UserModal, on_delete=models.CASCADE, related_name='author')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField(null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def score(self):
        score = self.comment_votes.aggregate(sum=Sum('vote'))['sum']
        return score or 0

    def __str__(self):
        return f"#{self.id} {self.author} commented on {self.post}"


class VoteComment(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'comment'], name='unique_comment_vote'),
        ]

    class VoteType(models.IntegerChoices):
        downvote = -1, _("Down Vote")
        upvote = 1, _("Up Vote")

    voter = models.ForeignKey(UserModal, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_votes')
    vote = models.IntegerField(choices=VoteType.choices)

    def __str__(self):
        return f"#{self.id} {self.voter} voted a comment by {self.comment.author}"

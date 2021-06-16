from rest_framework import serializers
from forums.models import Thread, Forum, Post
from .profiles import SimpleUserSerializer
from .competitions import CompetitionSerializerSimple
import logging

logger = logging.getLogger(__name__)


class ThreadCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=255, allow_blank=False)
    content = serializers.CharField(required=True, allow_blank=False)


class ForumSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializerSimple(many=False)

    class Meta:
        model = Forum
        fields = ('id', 'competition')


class PostSerializerSimple(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'content')


class ThreadDetailSerializer(serializers.ModelSerializer):
    started_by = SimpleUserSerializer(many=False)
    forum = ForumSerializer(many=False)
    posts = PostSerializerSimple(many=True)

    class Meta:
        model = Thread
        fields = (
            'id',
            'forum',
            'date_created',
            'started_by',
            'title',
            'last_post_date',
            'pinned_date',
            'posts'
        )


class PostDetailSerializer(serializers.ModelSerializer):
    posted_by = SimpleUserSerializer(many=False)

    class Meta:
        model = Post
        fields = (
            'id',
            'thread',
            'date_created',
            'posted_by',
            'content'
        )


class PostCreateSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, allow_blank=False)

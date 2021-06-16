from rest_framework import viewsets
from api.serializers.forums import ThreadCreateSerializer, ThreadDetailSerializer, PostDetailSerializer, PostCreateSerializer
from rest_framework.response import Response
from forums.models import Post, Thread, Forum
import datetime
import logging
from rest_framework.decorators import action
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)


class ForumViewSet(viewsets.ModelViewSet):

    queryset = Forum.objects.all()

    def retrieve(self, request, *args, **kwargs):
        forum = self.get_object()
        thread_list_sorted = Thread.objects.filter(forum=forum)\
            .order_by('pinned_date', '-date_created') \
            .select_related('forum', 'forum__competition', 'forum__competition__created_by', 'started_by') \
            .prefetch_related('forum__competition__collaborators', 'posts')
        serializer = ThreadDetailSerializer(thread_list_sorted, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def add_thread(self, request, pk):
        forum = self.get_object()
        serializer = ThreadCreateSerializer(data=request.data)
        if serializer.is_valid():
            thread = Thread.objects.create(
                forum=forum,
                started_by=self.request.user,
                title=serializer.data['title'],
                last_post_date=datetime.datetime.now()
            )
            Post.objects.create(
                thread=thread,
                content=serializer.data['content'],
                posted_by=self.request.user
            )
            return Response(status=201, data=serializer.data)
        else:
            return Response(status=400, data=serializer.errors)


@api_view(['GET'])
def forum_thread_detail(request, forum_pk, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    ordered_posts = thread.posts.all().order_by('date_created') \
        .select_related('thread__forum__competition__created_by', 'posted_by') \
        .prefetch_related('thread__forum__competition__collaborators')
    serializer = PostDetailSerializer(ordered_posts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_post(request, forum_pk, thread_pk):
    serializer = PostCreateSerializer(data=request.data)
    if serializer.is_valid():
        thread = Thread.objects.get(pk=thread_pk)
        post = Post(
            thread=thread,
            posted_by=request.user,
            content=serializer.data.get('content')
        )
        post.save()
        thread.last_post_date = datetime.datetime.now()
        thread.save()
        thread.notify_all_posters_of_new_post(post)
        return Response(status=201, data=serializer.data)
    else:
        return Response(status=400, data=serializer.errors)

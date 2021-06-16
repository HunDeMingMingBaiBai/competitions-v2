from django.conf.urls import include
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter
from rest_framework.permissions import AllowAny
from rest_framework.urlpatterns import format_suffix_patterns

from .views import analytics, competitions, datasets, profiles, leaderboards, submissions, tasks, queues, forums


router = SimpleRouter()
router.register('competitions', competitions.CompetitionViewSet)
router.register('phases', competitions.PhaseViewSet, 'phases')
router.register('submissions', submissions.SubmissionViewSet)
router.register('datasets', datasets.DataViewSet)
router.register('data_groups', datasets.DataGroupViewSet)
router.register('leaderboards', leaderboards.LeaderboardViewSet)
router.register('submission_scores', leaderboards.SubmissionScoreViewSet, 'submission_scores')
router.register('tasks', tasks.TaskViewSet)
router.register('participants', competitions.CompetitionParticipantViewSet, 'participants')
router.register('queues', queues.QueueViewSet, 'queues')
router.register('users', profiles.UserViewSet, 'users')
router.register('organizations', profiles.OrganizationViewSet, 'organizations')
router.register('forums', forums.ForumViewSet, 'forums')

schema_view = get_schema_view(
    openapi.Info(
        title="Codabench API",
        default_version='v1',
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('my_profile/', profiles.GetMyProfile.as_view()),
    path('datasets/completed/<uuid:key>/', datasets.upload_completed),
    path('upload_submission_scores/<int:submission_pk>/', submissions.upload_submission_scores),
    path('can_make_submission/<phase_id>/', submissions.can_make_submission, name="can_make_submission"),
    path('user_lookup/', profiles.user_lookup),
    path('analytics/', analytics.AnalyticsView.as_view(), name='analytics_api'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token),

    path('get_token/', profiles.get_token, name="get_token"),
    path('signup_site/', profiles.signup_site, name="signup_site"),
    path('login_site/', profiles.login_site, name='login_site'),
    path('logout_site/', profiles.logout_site, name='logout_site'),
    path('get_general_status', profiles.get_general_status, name="get_general_status"),
    path('forums/threads/<int:forum_pk>/<int:thread_pk>/', forums.forum_thread_detail),
    path('forums/threads/<int:forum_pk>/<int:thread_pk>/create_post/', forums.create_post),
    path('get_server_status/', profiles.get_server_status, name="get_server_status"),

    # API Docs
    re_path(r'docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Include this at the end so our URLs above run first, like /datasets/completed/<pk>/ before /datasets/<pk>/
    path('', include(format_suffix_patterns(router.urls, allowed=['html', 'json', 'csv', 'zip']))),
]

import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import permissions, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from rest_framework.decorators import api_view
from datetime import timedelta
from django.utils.timezone import now

from api.permissions import IsUserAdminOrIsSelf, IsOrganizationEditor
from api.serializers.profiles import MyProfileSerializer, UserSerializer, \
    OrganizationSerializer, MembershipSerializer, SimpleOrganizationSerializer, DeleteMembershipSerializer, OrganizationDetailSerializer
from profiles.helpers import send_mail
from profiles.models import Organization, Membership
from competitions.models import Submission
from api.serializers.competitions import ServerStatusSerializer

from django.contrib.auth import authenticate, login, logout
from utils.render_response import success_data

User = get_user_model()


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsUserAdminOrIsSelf]
        return [permission() for permission in self.permission_classes]

    def update(self, request, *args, **kwargs):
        print(request.user)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        resp = self.get_serializer(instance)
        return Response(data=resp.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def participant_organizations(self, request):
        memberships = request.user.membership_set.filter(group__in=Membership.PARTICIPANT_GROUP).prefetch_related('organization')
        data = SimpleOrganizationSerializer([member.organization for member in memberships], many=True).data
        return Response(data)


class GetMyProfile(RetrieveAPIView, GenericAPIView):
    # queryset = User.objects.all()
    serializer_class = MyProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


@login_required
def user_lookup(request):
    search = request.GET.get('q', '')
    filters = Q()
    is_admin = request.user.is_superuser or request.user.is_staff

    if search:
        filters |= Q(username__icontains=search)
        filters |= Q(email__icontains=search) if is_admin else Q(email__iexact=search)

    users = User.objects.exclude(id=request.user.id).filter(filters)[:5]

    # Helper to print username with email for admins
    def _get_data(user):
        return {
            "id": user.id,
            "name": f"{user.name or user.username} ({user.email})" if is_admin else user.username,
            "username": user.username,
        }

    return JsonResponse(
        success_data({"results": [_get_data(u) for u in users]}),
    )


class OrganizationViewSet(mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):

    def get_queryset(self):
        orgs = Organization.objects.all()
        if self.request.method in ['GET', 'LIST', 'CREATE']:
            return orgs
        elif self.request.method in ['PUT', 'PATCH', 'POST', 'DELETE']:
            return orgs.filter(users__in=[self.request.user])

    def get_serializer_class(self):
        return OrganizationSerializer

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'list']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOrganizationEditor]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)

        # Set Creator to Owner
        obj.users.add(request.user)
        member = obj.membership_set.first()
        member.group = Membership.OWNER
        member.save()
        obj.user_record.add(request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrganizationDetailSerializer(instance)
        data = {
            "organization": serializer.data
        }
        membership = instance.membership_set.filter(user=self.request.user)
        if len(membership) == 1:
            data['is_editor'] = membership.first().group in Membership.EDITORS_GROUP
        else:
            data['is_editor'] = False
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[IsOrganizationEditor])
    def update_member_group(self, request, pk=None):
        organization = self.get_object()
        try:
            member = organization.membership_set.get(pk=request.data['membership'])
        except Membership.DoesNotExist:
            raise ValidationError('Could not find organization member')
        if member.group == Membership.OWNER:
            raise PermissionDenied('Cannot change the organization Owner')
        if member.group == Membership.INVITED:
            raise PermissionDenied('The User must accept their invite before you can change their permissions')
        if request.data['group'] not in Membership.SETTABLE_PERMISSIONS:
            raise ValidationError(f'Cannot set a member to {request.data["group"]}.')
        member.group = request.data['group']
        member.save()
        return Response({f'Member{member.user} permission changed to {member.group}'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsOrganizationEditor])
    def invite_users(self, request, pk=None):
        org = self.get_object()
        if type(request.data['users']) != list:
            raise ValidationError(f'Required data is an Array of User ID\'s not a {type(request.data["users"])} ')
        # Getting users, but filtering out any that are already in the organization
        users = User.objects.filter(id__in=request.data['users']).exclude(organizations=pk)
        org.users.add(*users)
        # Getting membership so we can access invite token
        members = org.membership_set.filter(user__in=[user.id for user in users])
        for member in members:
            if member.user.allow_organization_invite_emails:
                send_mail(
                    context={
                        'user': member.user,
                        'invite_url': f'{reverse("profiles:organization_accept_invite")}?token={member.token}',
                        'organization': org.name,
                    },
                    subject=f'You have been invited to join {org.name}',
                    html_file="profiles/emails/invite.html",
                    text_file="profiles/emails/invite.txt",
                    to_email=member.user.email
                )

        return Response({})

    @action(detail=True, methods=['delete'], permission_classes=[IsOrganizationEditor])
    def delete_member(self, request, pk=None):
        ser = DeleteMembershipSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        organization = self.get_object()
        try:
            member = organization.membership_set.get(pk=request.data['membership'])
        except Membership.DoesNotExist:
            raise ValidationError('Could not find organization member')
        if member.group == Membership.OWNER:
            raise PermissionDenied('Cannot change the organization Owner')
        member.organization.users.remove(member.user)
        return Response('Member removed from Organization', status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def invite_response(self, request):
        token = request.data['token']
        try:
            membership = Membership.objects.get(token=token)
        except Membership.DoesNotExist:
            raise ValidationError('No Invite found')
        if membership.user != request.user:
            raise PermissionDenied('This invite was not sent to you. Make sure you are logged in as the right account')
        # If the invite has already been accepted, do nothing.
        if membership.user != request.user:
            resp = {
                'invite_status': 'already accepted',
                'redirect_url': reverse('profiles:organization_profile', args=[membership.organization_id])
            }
            return Response(resp, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            membership.organization.users.remove(request.user)
            return Response('Deleted Invite', status=status.HTTP_200_OK)

        elif request.method == 'POST':
            membership.group = Membership.MEMBER
            membership.save()
            membership.organization.user_record.add(request.user)
            resp = {
                'invite_status': 'accepted',
                'redirect_url': reverse('profiles:organization_profile', args=[membership.organization_id])
            }
            return Response(resp, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def validate_invite(self, request):
        token = request.data['token']
        try:
            membership = Membership.objects.get(token=token)
        except Membership.DoesNotExist:
            raise ValidationError('No Invite found')
        if membership.user != request.user:
            raise PermissionDenied('This invite was not sent to you. Make sure you are logged in as the right account')
        # TODO Should add some sort of system that deletes users that don't accept invites within a certain time period

        # If the User has already accept the invite, redirect them to the Organization page
        if membership.group != Membership.INVITED:
            url = reverse('profiles:organization_profile', args=[membership.organization_id])
            return Response({'redirect_url': url}, status=status.HTTP_301_MOVED_PERMANENTLY)

        mem_ser = MembershipSerializer(membership)
        return Response(mem_ser.data, status=status.HTTP_200_OK)


def get_token(request):
    from django.middleware.csrf import get_token
    token = get_token(request)
    return JsonResponse(data=success_data({'token': token}))


def signup_site(request):
    from profiles.forms import SignUpForm
    form = SignUpForm(json.loads(request.body))
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        serializer = UserSerializer(user)
        return JsonResponse(data=success_data({"user": serializer.data}))
    else:
        data = {
            "status": "fail",
            "fail_message": '',
            "error": form.errors,
        }
        return JsonResponse(data=data)


def login_site(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        serializer = UserSerializer(user)
        return JsonResponse(data=success_data({"user": serializer.data}))
    else:
        return JsonResponse(data={"status": "fail"})


def logout_site(request):
    logout(request)
    return JsonResponse(data={"status": "success"})


def get_general_status(request):
    from django.db.models import Count, Q
    from competitions.models import Competition, Submission, CompetitionParticipant

    data = Competition.objects.aggregate(
        count=Count('*'),
        published_comps=Count('pk', filter=Q(published=True)),
        unpublished_comps=Count('pk', filter=Q(published=False)),
    )

    total_competitions = data['count']
    public_competitions = data['published_comps']
    private_competitions = data['unpublished_comps']
    users = User.objects.all().count()
    competition_participants = CompetitionParticipant.objects.all().count()
    submissions = Submission.objects.all().count()

    general_stats = [
        {'label': "Total Competitions", 'count': total_competitions},
        {'label': "Public Competitions", 'count': public_competitions},
        {'label': "Private Competitions", 'count': private_competitions},
        {'label': "Users", 'count': users},
        {'label': "Competition Participants", 'count': competition_participants},
        {'label': "Submissions", 'count': submissions},
    ]
    return JsonResponse(data=success_data({'general_stats': general_stats}))


@api_view(['GET'])
def get_server_status(request):
    if not request.user.is_staff:
        raise Response(status=404)

    qs = Submission.objects.all()
    qs = qs.filter(created_when__gte=now() - timedelta(days=2))
    qs = qs.order_by('-created_when')
    qs = qs.select_related('phase__competition', 'owner')

    serializer = ServerStatusSerializer(qs[:250], many=True)
    return Response(serializer.data)

import logging
import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.timezone import now

from chahub.models import ChaHubSaveMixin
from leaderboards.models import SubmissionScore
from profiles.models import User, Organization
from utils.data import PathWrapper
from utils.storage import BundleStorage

from tasks.models import Task

logger = logging.getLogger()


class Competition(ChaHubSaveMixin, models.Model):
    COMPETITION = "competition"
    BENCHMARK = "benchmark"

    COMPETITION_TYPE = (
        (COMPETITION, "competition"),
        (BENCHMARK, "benchmark"),
    )

    title = models.CharField(max_length=256)
    logo = models.ImageField(upload_to=PathWrapper('logos'), null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="competitions")
    created_when = models.DateTimeField(default=now)
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="collaborations", blank=True)
    published = models.BooleanField(default=False)
    secret_key = models.UUIDField(default=uuid.uuid4, unique=True, null=True, blank=True)
    registration_auto_approve = models.BooleanField(default=False)
    terms = models.TextField(null=True, blank=True)
    is_migrating = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    docker_image = models.CharField(max_length=128, default="codalab/codalab-legacy:py3")
    enable_detailed_results = models.BooleanField(default=False)

    queue = models.ForeignKey('queues.Queue', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='competitions')

    allow_robot_submissions = models.BooleanField(default=False)
    # we use filed type to distinguish 'competition' and 'benchmark'
    competition_type = models.CharField(max_length=128, choices=COMPETITION_TYPE, default=COMPETITION)

    fact_sheet = JSONField(blank=True, null=True, max_length=4096, default=None)

    def __str__(self):
        return f"competition-{self.title}-{self.pk}-{self.competition_type}"

    @property
    def bundle_dataset(self):
        try:
            bundle = CompetitionCreationTaskStatus.objects.get(resulting_competition=self).dataset
        except CompetitionCreationTaskStatus.DoesNotExist:
            bundle = None
        return bundle

    @property
    def all_organizers(self):
        return [self.created_by] + list(self.collaborators.all())

    def user_has_admin_permission(self, user):
        if isinstance(user, int):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                return False
        if user.is_staff or user.is_superuser:
            return True
        else:
            return user in self.all_organizers

    def apply_phase_migration(self, current_phase, next_phase, force_migration=False):
        """
        Does the actual migrating of submissions from current_phase to next_phase

        :param force_migration: overrides check for currently running submissions
        :param current_phase: The phase object to transfer submissions from
        :param next_phase: The new phase object we are entering
        """

        if not force_migration:
            logger.info(f"Checking for submissions that may still be running competition pk={self.pk}")
            status_list = [Submission.CANCELLED, Submission.FINISHED, Submission.FAILED, Submission.NONE]
            if current_phase.submissions.exclude(status__in=status_list).exists():
                logger.info(f"Some submissions still marked as processing for competition pk={self.pk}")
                self.is_migrating_delayed = True
                self.save()
                return
            else:
                logger.info(f"No submissions running for competition pk={self.pk}")

        logger.info(f"Doing phase migration on competition pk={self.pk} "
                    f"from phase: {current_phase.index} to phase: {next_phase.index}")

        self.is_migrating = True
        self.save()

        submissions = Submission.objects.filter(
            phase=current_phase,
            is_migrated=False,
            parent__isnull=True,
            status=Submission.FINISHED
        )

        for submission in submissions:
            new_submission = Submission(
                created_by_migration=current_phase,
                participant=submission.participant,
                phase=next_phase,
                task=submission.task,
                owner=submission.owner,
                data=submission.data,
            )
            new_submission.save(ignore_submission_limit=True)
            new_submission.start()

            submission.is_migrated = True
            submission.save()

        # To check for submissions being migrated, does not allow to enter new submission
        next_phase.has_been_migrated = True
        next_phase.save()

        self.is_migrating_delayed = False
        self.save()

    def update_phase_statuses(self):
        current_phase = None
        for phase in self.phases.all():
            if phase.end is not None and phase.start < now() < phase.end:
                current_phase = phase
            elif phase.end is None:
                current_phase = phase

        if current_phase:
            current_index = current_phase.index
            previous_index = current_index - 1 if current_index >= 1 else None
            next_index = current_index + 1 if current_index < len(self.phases.all()) - 1 else None
        else:
            current_index = None

            next_phase = self.phases.filter(end__gt=now()).order_by('index').first()
            if next_phase:
                next_index = next_phase.index
                previous_index = next_index - 1 if next_index >= 1 else None
            else:
                next_index = None
                previous_index = None

        if current_index is not None:
            self.phases.filter(index=current_index).update(status=Phase.CURRENT)
        if next_index is not None:
            self.phases.filter(index=next_index).update(status=Phase.NEXT)
        if previous_index is not None:
            self.phases.filter(index=previous_index).update(status=Phase.PREVIOUS)

    def get_absolute_url(self):
        return reverse('competitions:detail', kwargs={'pk': self.pk})

    @staticmethod
    def get_chahub_endpoint():
        return "competitions/"

    def get_chahub_is_valid(self):
        has_phases = self.phases.exists()
        upload_finished = all([c.status == CompetitionCreationTaskStatus.FINISHED for c in
                               self.creation_statuses.all()]) if self.creation_statuses.exists() else True
        return has_phases and upload_finished

    def get_whitelist(self):
        return [
            'remote_id',
            'participants',
            'phases',
            'published',
        ]

    def get_chahub_data(self):
        data = {
            'created_by': self.created_by.username,
            'creator_id': self.created_by.pk,
            'created_when': self.created_when.isoformat(),
            'title': self.title,
            'url': f'http://{Site.objects.get_current().domain}{self.get_absolute_url()}',
            'remote_id': self.pk,
            'published': self.published,
            'participants': [p.get_chahub_data() for p in self.participants.all()],
            'phases': [phase.get_chahub_data(send_competition_id=False) for phase in self.phases.all()],
        }
        start = getattr(self.phases.order_by('index').first(), 'start', None)
        data['start'] = start.isoformat() if start is not None else None
        end = getattr(self.phases.order_by('index').last(), 'end', None)
        data['end'] = end.isoformat() if end is not None else None
        if self.logo:
            data['logo_url'] = self.logo.url
            data['logo'] = self.logo.url

        return self.clean_private_data(data)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        to_create = User.objects.filter(
            Q(id=self.created_by_id) | Q(id__in=self.collaborators.all().values_list('id', flat=True))
        ).exclude(id__in=self.participants.values_list('user_id', flat=True)).distinct()
        new_participants = []
        for user in to_create:
            new_participants.append(CompetitionParticipant(user=user, competition=self, status='approved'))
        if new_participants:
            CompetitionParticipant.objects.bulk_create(new_participants)


class CompetitionCreationTaskStatus(models.Model):
    STARTING = "Starting"
    FINISHED = "Finished"
    FAILED = "Failed"

    STATUS_CHOICES = (
        (STARTING, "None"),
        (FINISHED, "Finished"),
        (FAILED, "Failed"),
    )

    dataset = models.ForeignKey('datasets.Data', on_delete=models.SET_NULL, null=True, related_name="competition_bundles")
    status = models.TextField(choices=STATUS_CHOICES, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='competition_creation_task_statuses',
    )

    # The resulting competition is only made on success
    resulting_competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, blank=True,
                                              related_name='creation_statuses')

    def __str__(self):
        return f"pk: {self.pk} ({self.status})"


class Phase(ChaHubSaveMixin, models.Model):
    PREVIOUS = "Previous"
    CURRENT = "Current"
    NEXT = "Next"
    FINAL = "Final"

    STATUS_CHOICES = (
        (PREVIOUS, "Previous"),
        (CURRENT, "Current"),
        (NEXT, "Next"),
    )

    status = models.TextField(choices=STATUS_CHOICES, null=True, blank=True)
    is_final_phase = models.BooleanField(default=False)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, blank=True, related_name='phases')
    index = models.PositiveIntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    execution_time_limit = models.PositiveIntegerField(default=60 * 10)
    auto_migrate_to_this_phase = models.BooleanField(default=False)
    has_been_migrated = models.BooleanField(default=False)
    hide_output = models.BooleanField(default=False)

    has_max_submissions = models.BooleanField(default=False)
    max_submissions_per_day = models.PositiveIntegerField(null=True, blank=True)
    max_submissions_per_person = models.PositiveIntegerField(null=True, blank=True)

    tasks = models.ManyToManyField('tasks.Task', blank=True, related_name='phases', through='PhaseTaskInstance')

    leaderboard = models.ForeignKey('leaderboards.Leaderboard', on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name="phases")

    class Meta:
        ordering = ('index',)

    def __str__(self):
        return f"phase - {self.name} - For comp: {self.competition.title} - ({self.id})"

    @property
    def published(self):
        return self.competition.published

    def can_user_make_submissions(self, user):
        """Takes a user and checks how many submissions they've made vs the max.

        Returns:
            (can_make_submissions, reason_if_not)
        """
        if not self.has_max_submissions or (user.is_bot and self.competition.allow_robot_submissions):
            return True, None

        qs = self.submissions.filter(owner=user, parent__isnull=True).exclude(status='Failed')
        total_submission_count = qs.count()
        daily_submission_count = qs.filter(created_when__day=now().day).count()

        if self.max_submissions_per_day:
            if daily_submission_count >= self.max_submissions_per_day:
                return False, 'Reached maximum allowed submissions for today for this phase'
        if self.max_submissions_per_person:
            if total_submission_count >= self.max_submissions_per_person:
                return False, 'Reached maximum allowed submissions for this phase'
        return True, None

    @staticmethod
    def get_chahub_endpoint():
        return 'phases/'

    def get_whitelist(self):
        return ['remote_id', 'published', 'tasks', 'index', 'status', 'competition_remote_id']

    def get_chahub_data(self, send_competition_id=True):
        data = {
            'remote_id': self.pk,
            'published': self.published,
            'status': self.status,
            'index': self.index,
            'start': self.start.isoformat(),
            'end': self.end.isoformat() if self.end else None,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'tasks': [task.get_chahub_data() for task in self.tasks.all()]
        }
        if send_competition_id:
            data['competition_remote_id'] = self.competition.pk
        return self.clean_private_data(data)

    @property
    def is_active(self):
        """ Returns true when this phase of the competition is on-going. """
        if not self.end:
            return True
        else:
            return self.start < now() < self.end

    def check_future_phase_submissions(self):
        """
        Checks for if we need to migrate current phase submissions to next phase.
        """
        current_phase = self.competition.phases.get(index=self.index - 1)
        next_phase = self

        # Check for next phase and see if it has auto_migration enabled
        try:
            if not next_phase.has_been_migrated:
                logger.info(
                    f"Checking for needed migrations on competition pk={self.competition.pk}, "
                    f"current phase: {current_phase.index}, next phase: {next_phase.index}")
                self.competition.apply_phase_migration(current_phase, next_phase)

        except next_phase.DoesNotExist:
            logger.info(f"This competition is missing the next phase to migrate to.")
        except current_phase.DoesNotExist:
            logger.info(f"This competition is missing the previous phase to migrate from.")


class PhaseTaskInstance(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name="task_instances")
    order_index = models.PositiveIntegerField(default=999)

    class Meta:
        ordering = ["order_index", "task"]

    def __str__(self):
        return f'Task:{self.task.name}, Phase:{self.phase.name}, Order:{int(self.order_index)}'


class SubmissionDetails(models.Model):
    DETAILED_OUTPUT_NAMES_PREDICTION = [
        "prediction_stdout",
        "prediction_stderr",
        "prediction_ingestion_stdout",
        "prediction_ingestion_stderr",
    ]
    DETAILED_OUTPUT_NAMES_SCORING = [
        "scoring_stdout",
        "scoring_stderr",
        "scoring_ingestion_stdout",
        "scoring_ingestion_stderr",
    ]
    name = models.CharField(max_length=50)
    data_file = models.FileField(upload_to=PathWrapper('submission_details'), storage=BundleStorage)
    submission = models.ForeignKey('Submission', on_delete=models.CASCADE, related_name='details')
    is_scoring = models.BooleanField(default=False)


class Submission(ChaHubSaveMixin, models.Model):
    NONE = "None"
    SUBMITTING = "Submitting"
    SUBMITTED = "Submitted"
    PREPARING = "Preparing"
    RUNNING = "Running"
    SCORING = "Scoring"
    CANCELLED = "Cancelled"
    FINISHED = "Finished"
    FAILED = "Failed"

    STATUS_CHOICES = (
        (NONE, "None"),
        (SUBMITTING, "Submitting"),
        (SUBMITTED, "Submitted"),
        (PREPARING, "Preparing"),
        (RUNNING, "Running"),
        (SCORING, "Scoring"),
        (CANCELLED, "Cancelled"),
        (FINISHED, "Finished"),
        (FAILED, "Failed"),
    )

    description = models.CharField(max_length=240, default="", blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submission', on_delete=models.DO_NOTHING)
    organization = models.ForeignKey(Organization, related_name='submissions', on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default=SUBMITTING, null=False, blank=False)
    status_details = models.TextField(null=True, blank=True)
    phase = models.ForeignKey(Phase, related_name='submissions', on_delete=models.CASCADE)
    appear_on_leaderboards = models.BooleanField(default=False)
    data = models.ForeignKey("datasets.Data", on_delete=models.CASCADE, related_name='submission')
    md5 = models.CharField(max_length=32, null=True, blank=True)

    prediction_result = models.FileField(upload_to=PathWrapper('prediction_result'), null=True, blank=True,
                                         storage=BundleStorage)
    scoring_result = models.FileField(upload_to=PathWrapper('scoring_result'), null=True, blank=True,
                                      storage=BundleStorage)
    detailed_result = models.FileField(upload_to=PathWrapper('detailed_result'), null=True, blank=True,
                                       storage=BundleStorage)

    secret = models.UUIDField(default=uuid.uuid4)
    celery_task_id = models.UUIDField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.PROTECT, null=True, blank=True, related_name="submissions")
    leaderboard = models.ForeignKey("leaderboards.Leaderboard", on_delete=models.SET_NULL, related_name="submissions",
                                    null=True, blank=True)

    # Experimental
    name = models.CharField(max_length=120, default="", null=True, blank=True)
    participant = models.ForeignKey('CompetitionParticipant', related_name='submissions', on_delete=models.CASCADE,
                                    null=True, blank=True)
    created_when = models.DateTimeField(default=now)
    started_when = models.DateTimeField(null=True)
    is_public = models.BooleanField(default=False)
    is_specific_task_re_run = models.BooleanField(default=False)

    is_migrated = models.BooleanField(default=False)
    created_by_migration = models.ForeignKey(Phase, related_name='migrated_submissions', on_delete=models.CASCADE,
                                             null=True,
                                             blank=True)

    scores = models.ManyToManyField('leaderboards.SubmissionScore', related_name='submissions')

    has_children = models.BooleanField(default=False)
    parent = models.ForeignKey('Submission', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    fact_sheet_answers = JSONField(null=True, blank=True, max_length=4096)

    def __str__(self):
        return f"{self.phase.competition.title} submission PK={self.pk} by {self.owner.username}"

    def delete(self, **kwargs):
        # Also clean up details on delete
        self.details.all().delete()
        # Call this here so that the data_file for the submission also gets deleted from storage
        self.data.delete()
        super().delete(**kwargs)

    def save(self, ignore_submission_limit=False, **kwargs):
        created = not self.pk
        if created and not ignore_submission_limit:
            can_make_submission, reason_why_not = self.phase.can_user_make_submissions(self.owner)
            if not can_make_submission:
                raise PermissionError(reason_why_not)

        if self.status == Submission.RUNNING and not self.started_when:
            self.started_when = now()

        super().save(**kwargs)

    def start(self, tasks=None):
        from .tasks import run_submission
        run_submission(self.pk, tasks=tasks)

    def re_run(self, task=None):
        submission_arg_dict = {
            'owner': self.owner,
            'task': task or self.task,
            'phase': self.phase,
            'data': self.data,
            'has_children': self.has_children,
            'is_specific_task_re_run': bool(task),
            'fact_sheet_answers': self.fact_sheet_answers,
        }
        sub = Submission(**submission_arg_dict)
        sub.save(ignore_submission_limit=True)

        # No need to rerun on children if this is running on a specific task
        if not self.has_children or sub.is_specific_task_re_run:
            self.refresh_from_db()
            tasks = [sub.task]
        else:
            tasks = Task.objects.filter(pk__in=self.children.values_list('task', flat=True))
        sub.start(tasks=tasks)
        return sub

    def cancel(self, status=CANCELLED):
        if self.status not in [Submission.CANCELLED, Submission.FAILED, Submission.FINISHED]:
            if self.has_children:
                for sub in self.children.all():
                    sub.cancel(status=status)
            self.status = status
            self.save()
            return True
        return False

    def check_child_submission_statuses(self):
        done_statuses = [self.FINISHED, self.FAILED, self.CANCELLED]
        if all([status in done_statuses for status in self.children.values_list('status', flat=True)]):
            self.status = 'Finished'
            self.save()

    def calculate_scores(self):
        # leaderboards = self.phase.competition.leaderboards.all()
        # for leaderboard in leaderboards:
        columns = self.phase.leaderboard.columns.exclude(computation__isnull=True)
        for column in columns:
            scores = self.scores.filter(column__index__in=column.computation_indexes.split(',')).values_list('score',
                                                                                                             flat=True)
            if scores.exists():
                score = column.compute(scores)
                try:
                    sub_score = self.scores.get(column=column)
                    sub_score.score = score
                    sub_score.save()
                except SubmissionScore.DoesNotExist:
                    sub_score = SubmissionScore.objects.create(
                        column=column,
                        score=score
                    )
                    self.scores.add(sub_score)

    @property
    def on_leaderboard(self):
        on_leaderboard = False
        if self.leaderboard:
            on_leaderboard = True
        elif self.has_children:
            on_leaderboard = bool(self.children.first().leaderboard)
        return on_leaderboard

    @staticmethod
    def get_chahub_endpoint():
        return "submissions/"

    def get_whitelist(self):
        return [
            'remote_id',
            'is_public',
            'competition',
            'phase_index',
            'data',
        ]

    def get_chahub_data(self):
        data = {
            "remote_id": self.id,
            "is_public": self.is_public,
            "competition": self.phase.competition_id,
            "phase_index": self.phase.index,
            "owner": self.owner.id,
            "participant_name": self.owner.username,
            "submitted_at": self.created_when.isoformat(),
            "data": self.data.get_chahub_data(),
        }
        return self.clean_private_data(data)

    def get_chahub_is_valid(self):
        return self.status == self.FINISHED


class CompetitionParticipant(ChaHubSaveMixin, models.Model):
    UNKNOWN = 'unknown'
    DENIED = 'denied'
    APPROVED = 'approved'
    PENDING = 'pending'

    STATUS_CHOICES = (
        (UNKNOWN, 'unknown'),
        (DENIED, 'denied'),
        (APPROVED, 'approved'),
        (PENDING, 'pending'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, related_name='competitions_im_in',
                             on_delete=models.DO_NOTHING)
    competition = models.ForeignKey(Competition, related_name='participants', on_delete=models.CASCADE)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, null=False, blank=False, default=UNKNOWN)
    reason = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'competition')

    def __str__(self):
        return f"({self.id}) - User: {self.user.username} in Competition: {self.competition.title}"

    @staticmethod
    def get_chahub_endpoint():
        return 'participants/'

    def get_whitelist(self):
        return [
            'remote_id',
            'competition_id'
        ]

    def get_chahub_data(self):
        data = {
            'remote_id': self.pk,
            'user': self.user.id,
            'status': self.status,
            'competition_id': self.competition_id
        }
        return self.clean_private_data(data)


class Page(models.Model):
    competition = models.ForeignKey(Competition, related_name='pages', on_delete=models.CASCADE)
    title = models.TextField(max_length=255)
    content = models.TextField(null=True, blank=True)
    index = models.PositiveIntegerField()

    class Meta:
        ordering = ('index',)


class CompetitionDump(models.Model):
    STARTING = "Starting"
    FINISHED = "Finished"
    FAILED = "Failed"

    STATUS_CHOICES = (
        (STARTING, "None"),
        (FINISHED, "Finished"),
        (FAILED, "Failed"),
    )

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='dumps')
    dataset = models.ForeignKey('datasets.Data', on_delete=models.CASCADE, related_name="competition_dump_file")
    status = models.TextField(choices=STATUS_CHOICES, null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    # The resulting competition is only made on success
    # resulting_competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Comp dump created by {self.dataset.created_by} - {self.status}"

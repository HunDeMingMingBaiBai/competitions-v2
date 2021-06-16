import logging
import os
import django
from django.conf import settings

django.setup()

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

logger = logging.getLogger()

from competitions.tasks import do_phase_migrations, update_phase_statuses, submission_status_cleanup

scheduler = BlockingScheduler(timezone=settings.TIME_ZONE, logger=logger)
scheduler.add_jobstore(DjangoJobStore(), "default")
scheduler.add_job(do_phase_migrations,
                  trigger=IntervalTrigger(seconds=300),
                  id="do_phase_migrations",
                  max_instances=1,
                  replace_existing=True,
                  )
logger.info("Added job 'do_phase_migrations'.")
scheduler.add_job(update_phase_statuses,
                  trigger=IntervalTrigger(seconds=3600),
                  id="update_phase_statuses",
                  max_instances=1,
                  replace_existing=True,
                  )
logger.info("Added job 'update_phase_statuses'.")
scheduler.add_job(submission_status_cleanup,
                  trigger=IntervalTrigger(seconds=3600),
                  id="submission_status_cleanup",
                  max_instances=1,
                  replace_existing=True,
                  )
logger.info("Added job 'submission_status_cleanup'.")
try:
    logger.info("Starting scheduler...")
    scheduler.start()
except KeyboardInterrupt:
    logger.info("Stopping scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler shut down successfully!")

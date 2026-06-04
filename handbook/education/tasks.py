from celery import shared_task
from education.models import (
    Submission,
    SubmissionStatus,
    UserProgress,
    ProgressStatus
)

import logging, time 

from education.websocket import send_submission_update

logger = logging.getLogger(__name__)


@shared_task
def check_submission(submission_id):
    time.sleep(5)
    try:
        submission = Submission.objects.get(pk=submission_id)
    except Submission.DoesNotExist:
        logger.warning(
            "Submission not found: %s",
            submission_id
        )
        return

    logger.info(
        "Processing submission %s",
        submission_id
    )

    if submission.code == "print(5)":
        submission.status = SubmissionStatus.DONE
        submission.save(update_fields=["status"])
        
        send_submission_update(submission)

        UserProgress.objects.filter(
            user=submission.user,
            task=submission.task
        ).exclude(
            status=ProgressStatus.COMPLETED
        ).update(
            status=ProgressStatus.COMPLETED
        )

        logger.info(
            "Submission %s completed successfully",
            submission_id
        )

    else:
        submission.status = SubmissionStatus.FAILED
        submission.save(update_fields=["status"])
        
        send_submission_update(submission)

        logger.info(
            "Submission %s failed",
            submission_id
        )
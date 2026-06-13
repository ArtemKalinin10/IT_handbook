import json
import docker


from celery import shared_task
from education.models import (
    Submission,
    SubmissionStatus,
    UserProgress,
    ProgressStatus
)

import logging

from django.utils.timezone import now
from education.websocket import send_submission_update

logger = logging.getLogger(__name__)


def get_docker_client():
    return docker.from_env()

def run_submission(code: str, tests: list[dict], time_limit_code: int, mem_limit_code: int):
    client = get_docker_client()
    payload = json.dumps({
        "time_limit_code": time_limit_code,
        "mem_limit_code": mem_limit_code,
        "code": code,
        "tests": tests
    })

    container = client.containers.run(
        "python-sandbox:latest",
        detach=True,
        network_disabled=True,
        mem_limit="256m",
        pids_limit=64,
        security_opt=["no-new-privileges"],
        stdin_open=True,
        stdout=True,
        stderr=True,
        tty=False,
        environment={"PYTHONUNBUFFERED": "1"}
    )

    socket = None

    try:
        socket = container.attach_socket(params={"stdin": 1, "stream": 1})
        socket._sock.send(payload.encode() + b"\n")
        socket.close()
        socket = None

        container.wait(timeout=30)
        logs = container.logs().decode()
        return json.loads(logs)

    except (ValueError, json.JSONDecodeError):
        logger.error("Invalid JSON from runner: %s", logs)
        return {"error": "invalid_json", "raw": logs}

    except Exception as e:
        return {"error": str(e)}

    finally:
        if socket:
            try:
                socket.close()
            except Exception:
                pass
        try:
            container.remove(force=True)
        except Exception:
            pass

@shared_task
def check_submission(submission_id):
    try:
        submission = (
            Submission.objects
            .select_related("task")
            .prefetch_related("task__tests")
            .get(pk=submission_id)
        )
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
    
    tests = submission.task.tests.all()
    time_limit = submission.task.execution_time_limit
    mem_limit = submission.task.size_limit
    
    payload_tests = [
        {
            "id": test.id,
            "input_data": test.input_data.replace("\r\n", "\n"),
            "expected_output": test.expected_output.replace("\r\n", "\n")
        }
        for test in tests
    ]
    
    result = run_submission(submission.code, payload_tests, time_limit, mem_limit)
    logger.info("Runner result: %s", result)
    
    if result["status"] == "OK":
        submission.status = SubmissionStatus.DONE
        submission.save(update_fields=["status"])
        
        send_submission_update(submission)

        UserProgress.objects.filter(
            user=submission.user,
            task=submission.task
        ).exclude(
            status=ProgressStatus.COMPLETED
        ).update(
            status=ProgressStatus.COMPLETED,
            completed_at=now()
        )

        logger.info(
            "Submission %s completed successfully",
            submission_id,
        )

    else:
        submission.status = SubmissionStatus.FAILED
        submission.save(update_fields=["status"])
        
        send_submission_update(submission)

        logger.info(
            "Submission %s failed",
            submission_id
        )
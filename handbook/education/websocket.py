from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_submission_update(submission):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"task_{submission.task_id}_user_{submission.user_id}",
        {
            "type": "submission_update",
            "submission_id": submission.id,
            "status": submission.status,
        }
    )
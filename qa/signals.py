from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Question, AppSetting


def _broadcast(group: str, reason: str):
    layer = get_channel_layer()
    if not layer:
        return
    async_to_sync(layer.group_send)(
        group,
        {"type": "broadcast.refresh", "reason": reason},
    )


@receiver(post_save, sender=Question)
def question_saved(sender, instance: Question, created, **kwargs):
    # Moderation page needs to update when new question comes or status changes
    _broadcast("moderators", "question_saved")
    # Screen updates when approved list changes
    _broadcast("screens", "question_saved")


@receiver(post_delete, sender=Question)
def question_deleted(sender, instance: Question, **kwargs):
    _broadcast("moderators", "question_deleted")
    _broadcast("screens", "question_deleted")


@receiver(post_save, sender=AppSetting)
def settings_saved(sender, instance: AppSetting, created, **kwargs):
    # Settings affect both screen and moderation UI
    _broadcast("screens", "settings_saved")
    _broadcast("moderators", "settings_saved")

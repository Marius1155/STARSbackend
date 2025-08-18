import strawberry
import asyncio
from typing import AsyncGenerator
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from STARS import models
from . import types


# -----------------------------------------------------------------------------
# Subscription Payload Types
# -----------------------------------------------------------------------------

@strawberry.type
class MessageEventPayload:
    event_type: str
    message: types.Message


@strawberry.type
class ConversationEventPayload:
    conversation: types.Conversation


# -----------------------------------------------------------------------------
# Subscription Resolvers
# -----------------------------------------------------------------------------

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def message_events(self, info, conversation_id: int) -> AsyncGenerator[MessageEventPayload, None]:
        # TEMPORARY: fallback user
        user = info.context.get("user")
        if not user or not user.is_authenticated:
            try:
                user = await database_sync_to_async(models.User.objects.get)(id=1)
            except models.User.DoesNotExist:
                raise ValueError("Fallback user with ID=1 not found.")

        # Check access safely
        def check_access():
            return models.Conversation.objects.filter(id=conversation_id, participants=user).exists()
        has_access = await database_sync_to_async(check_access)()
        if not has_access:
            raise ValueError("Access denied or conversation not found.")

        channel_layer = get_channel_layer()
        group_name = f"conversation_{conversation_id}"
        channel_name = await channel_layer.new_channel()
        await channel_layer.group_add(group_name, channel_name)

        try:
            while True:
                event = await channel_layer.receive(channel_name)
                event_type = event["data"]["event_type"]
                message_id = event["data"]["id"]

                # Safe DB access
                def get_message():
                    return models.Message.objects.filter(id=message_id).first()
                message_obj = await database_sync_to_async(get_message)()

                if message_obj:
                    yield MessageEventPayload(event_type=event_type, message=message_obj)
        finally:
            await channel_layer.group_discard(group_name, channel_name)

    @strawberry.subscription
    async def conversation_updates(self, info) -> AsyncGenerator[ConversationEventPayload, None]:
        user = info.context.get("user")
        if not user or not user.is_authenticated:
            try:
                user = await database_sync_to_async(models.User.objects.get)(id=1)
            except models.User.DoesNotExist:
                raise ValueError("Fallback user with ID=1 not found.")

        channel_layer = get_channel_layer()
        group_name = f"user_{user.id}_conversations"
        channel_name = await channel_layer.new_channel()
        await channel_layer.group_add(group_name, channel_name)

        try:
            while True:
                event = await channel_layer.receive(channel_name)
                conversation_id = event["data"]["id"]

                def get_conversation():
                    return models.Conversation.objects.get(id=conversation_id)
                conversation_obj = await database_sync_to_async(get_conversation)()

                yield ConversationEventPayload(conversation=conversation_obj)
        finally:
            await channel_layer.group_discard(group_name, channel_name)


# -----------------------------------------------------------------------------
# Signal Handlers & Broadcast Functions
# -----------------------------------------------------------------------------

@receiver(post_save, sender=models.Message)
def handle_message_save(sender, instance, created, update_fields, **kwargs):
    if created:
        async_to_sync(broadcast_message_event)(instance, "created")
    elif update_fields and ('is_read' in update_fields or 'is_delivered' in update_fields):
        async_to_sync(broadcast_message_event)(instance, "updated")


@receiver(m2m_changed, sender=models.Message.liked_by.through)
def handle_message_like(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        async_to_sync(broadcast_message_event)(instance, "updated")


@receiver(post_delete, sender=models.Message)
def handle_message_delete(sender, instance, **kwargs):
    async_to_sync(broadcast_message_event)(instance, "deleted")


async def broadcast_message_event(message: models.Message, event_type: str):
    channel_layer = get_channel_layer()
    group_name = f"conversation_{message.conversation_id}"

    def create_payload():
        return {"id": message.id, "event_type": event_type}

    await channel_layer.group_send(
        group_name,
        {"type": "subscription.event", "data": await database_sync_to_async(create_payload)()},
    )


@receiver(post_save, sender=models.Conversation)
def handle_conversation_save(sender, instance, created, update_fields, **kwargs):
    if not created and update_fields and 'latest_message' in update_fields:
        async_to_sync(broadcast_conversation_update)(instance)


async def broadcast_conversation_update(conversation: models.Conversation):
    channel_layer = get_channel_layer()

    def get_participant_ids():
        return list(conversation.participants.values_list('id', flat=True))

    participant_ids = await database_sync_to_async(get_participant_ids)()

    for user_id in participant_ids:
        group_name = f"user_{user_id}_conversations"
        await channel_layer.group_send(
            group_name,
            {"type": "subscription.event", "data": {"id": conversation.id}},
        )
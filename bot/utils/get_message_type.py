from telegram import Message
from typing import Literal

MessageType = Literal[
    "text",
    "audio",
    "animation",
    "document",
    "photo",
    "sticker",
    "story",
    "video",
    "video_note",
    "voice",
    "contact",
    "dice",
    "game",
    "poll",
    "venue",
    "location",
    "new_chat_members",
    "left_chat_member",
    "new_chat_title",
    "new_chat_photo",
    "delete_chat_photo",
    "group_chat_created",
    "supergroup_chat_created",
    "channel_chat_created",
    "message_auto_delete_timer_changed",
    "migrate_to_chat_id",
    "migrate_from_chat_id",
    "pinned_message",
    "invoice",
    "successful_payment",
    "user_shared",
    "chat_shared",
    "connected_website",
    "write_access_allowed",
    "passport_data",
    "proximity_alert_triggered",
    "forum_topic_created",
    "forum_topic_edited",
    "forum_topic_closed",
    "forum_topic_reopened",
    "general_forum_topic_hidden",
    "general_forum_topic_unhidden",
    "video_chat_scheduled",
    "video_chat_started",
    "video_chat_ended",
    "video_chat_participants_invited",
    "web_app_data",
    "unknown",
]


def get_message_type(message: Message) -> MessageType:
    print("get_message_type function called")

    if message.text:
        return "text"
    elif message.audio:
        return "audio"
    elif message.animation:
        return "animation"
    elif message.document:
        return "document"
    elif message.photo:
        return "photo"
    elif message.sticker:
        return "sticker"
    elif hasattr(
        message, "story"
    ):  # 'story' might not be available in all python-telegram-bot versions
        return "story"
    elif message.video:
        return "video"
    elif message.video_note:
        return "video_note"
    elif message.voice:
        return "voice"
    elif message.contact:
        return "contact"
    elif message.dice:
        return "dice"
    elif message.game:
        return "game"
    elif message.poll:
        return "poll"
    elif message.venue:
        return "venue"
    elif message.location:
        return "location"
    elif message.new_chat_members:
        return "new_chat_members"
    elif message.left_chat_member:
        return "left_chat_member"
    elif message.new_chat_title:
        return "new_chat_title"
    elif message.new_chat_photo:
        return "new_chat_photo"
    elif message.delete_chat_photo:
        return "delete_chat_photo"
    elif message.group_chat_created:
        return "group_chat_created"
    elif message.supergroup_chat_created:
        return "supergroup_chat_created"
    elif message.channel_chat_created:
        return "channel_chat_created"
    elif message.message_auto_delete_timer_changed:
        return "message_auto_delete_timer_changed"
    elif message.migrate_to_chat_id:
        return "migrate_to_chat_id"
    elif message.migrate_from_chat_id:
        return "migrate_from_chat_id"
    elif message.pinned_message:
        return "pinned_message"
    elif message.invoice:
        return "invoice"
    elif message.successful_payment:
        return "successful_payment"
    elif hasattr(
        message, "user_shared"
    ):  # These might not be available in all python-telegram-bot versions
        return "user_shared"
    elif hasattr(message, "chat_shared"):
        return "chat_shared"
    elif message.connected_website:
        return "connected_website"
    elif hasattr(message, "write_access_allowed"):
        return "write_access_allowed"
    elif message.passport_data:
        return "passport_data"
    elif message.proximity_alert_triggered:
        return "proximity_alert_triggered"
    elif hasattr(message, "forum_topic_created"):
        return "forum_topic_created"
    elif hasattr(message, "forum_topic_edited"):
        return "forum_topic_edited"
    elif hasattr(message, "forum_topic_closed"):
        return "forum_topic_closed"
    elif hasattr(message, "forum_topic_reopened"):
        return "forum_topic_reopened"
    elif hasattr(message, "general_forum_topic_hidden"):
        return "general_forum_topic_hidden"
    elif hasattr(message, "general_forum_topic_unhidden"):
        return "general_forum_topic_unhidden"
    elif hasattr(message, "video_chat_scheduled"):
        return "video_chat_scheduled"
    elif hasattr(message, "video_chat_started"):
        return "video_chat_started"
    elif hasattr(message, "video_chat_ended"):
        return "video_chat_ended"
    elif hasattr(message, "video_chat_participants_invited"):
        return "video_chat_participants_invited"
    elif hasattr(message, "web_app_data"):
        return "web_app_data"
    else:
        return "unknown"

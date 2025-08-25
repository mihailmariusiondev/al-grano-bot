# bot/utils/admin_notifications.py
"""
Centralized admin notification system.
Ensures admins are notified of all critical errors.
"""

from typing import Optional, List
from telegram.ext import ContextTypes
from ..utils.logger import logger

logger_instance = logger.get_logger(__name__)

async def notify_admins_critical(
    context: ContextTypes.DEFAULT_TYPE, 
    error_title: str,
    error_details: str,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None
) -> None:
    """
    Notify all admin users about critical system errors.
    
    Args:
        context: Telegram context for sending messages
        error_title: Brief title of the error (e.g., "Database Connection Failed")
        error_details: Detailed error information for debugging
        user_id: User ID where error occurred (optional)
        chat_id: Chat ID where error occurred (optional)
    """
    try:
        # Import here to avoid circular import
        from ..services.database_service import db_service
        admin_users = await db_service.get_admin_users()
        
        if not admin_users:
            logger_instance.critical("No admin users found in database - cannot send notifications!")
            return
            
        # Format notification message
        notification_parts = [
            f"🚨 **CRITICAL ERROR ALERT**",
            f"**Error:** {error_title}",
            f"**Details:** {error_details}",
        ]
        
        if user_id:
            notification_parts.append(f"**User ID:** {user_id}")
        if chat_id:
            notification_parts.append(f"**Chat ID:** {chat_id}")
            
        notification_parts.append(f"**Time:** {logger_instance.handlers[0].formatter.formatTime(logger_instance.makeRecord('admin', 20, '', 0, '', (), None))}")
        
        notification_message = "\n".join(notification_parts)
        
        # Send to all admins
        successful_notifications = 0
        for admin_id in admin_users:
            try:
                await context.bot.send_message(
                    chat_id=admin_id, 
                    text=notification_message,
                    parse_mode="Markdown"
                )
                successful_notifications += 1
                logger_instance.info(f"Critical error notification sent to admin {admin_id}")
            except Exception as send_error:
                logger_instance.error(f"Failed to notify admin {admin_id}: {send_error}")
                
        if successful_notifications == 0:
            logger_instance.critical(f"Failed to notify any admin about: {error_title}")
        else:
            logger_instance.info(f"Successfully notified {successful_notifications}/{len(admin_users)} admins")
            
    except Exception as notification_error:
        logger_instance.critical(f"Critical failure in admin notification system: {notification_error}")

async def notify_admins_warning(
    context: ContextTypes.DEFAULT_TYPE,
    warning_title: str, 
    warning_details: str,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None
) -> None:
    """
    Notify admins about important but non-critical issues.
    
    Args:
        context: Telegram context for sending messages
        warning_title: Brief title of the warning
        warning_details: Detailed warning information
        user_id: User ID where warning occurred (optional)
        chat_id: Chat ID where warning occurred (optional)
    """
    try:
        # Import here to avoid circular import
        from ..services.database_service import db_service
        admin_users = await db_service.get_admin_users()
        
        if not admin_users:
            logger_instance.warning("No admin users found - cannot send warning notifications")
            return
            
        # Format warning message
        notification_parts = [
            f"⚠️ **SYSTEM WARNING**",
            f"**Warning:** {warning_title}",
            f"**Details:** {warning_details}",
        ]
        
        if user_id:
            notification_parts.append(f"**User ID:** {user_id}")
        if chat_id:
            notification_parts.append(f"**Chat ID:** {chat_id}")
            
        notification_message = "\n".join(notification_parts)
        
        # Send to all admins (only first admin for warnings to avoid spam)
        admin_id = admin_users[0]
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=notification_message, 
                parse_mode="Markdown"
            )
            logger_instance.info(f"Warning notification sent to admin {admin_id}")
        except Exception as send_error:
            logger_instance.error(f"Failed to send warning to admin {admin_id}: {send_error}")
            
    except Exception as notification_error:
        logger_instance.error(f"Failure in admin warning notification: {notification_error}")

async def notify_admins_rate_limit(
    context: ContextTypes.DEFAULT_TYPE,
    model_name: str,
    fallback_used: Optional[str] = None
) -> None:
    """
    Notify admins about rate limit issues and fallback usage.
    """
    if fallback_used:
        title = f"Rate Limit - Fallback Used"
        details = f"Model '{model_name}' hit rate limit. Successfully switched to '{fallback_used}'"
        await notify_admins_warning(context, title, details)
    else:
        title = f"All Models Rate Limited"
        details = f"All fallback models exhausted starting with '{model_name}'. Service temporarily unavailable."
        await notify_admins_critical(context, title, details)

async def notify_admins_database_error(
    context: ContextTypes.DEFAULT_TYPE,
    operation: str,
    error_details: str,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None
) -> None:
    """
    Notify admins about database operation failures.
    """
    title = f"Database Error - {operation}"
    await notify_admins_critical(context, title, error_details, user_id, chat_id)

async def notify_admins_service_error(
    context: ContextTypes.DEFAULT_TYPE,
    service_name: str,
    error_details: str,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None
) -> None:
    """
    Notify admins about service failures (OpenAI, Daily Summary, etc.)
    """
    title = f"Service Error - {service_name}"
    await notify_admins_critical(context, title, error_details, user_id, chat_id)
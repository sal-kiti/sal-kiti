"""
Send email notifications
"""

import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail.message import BadHeaderError
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_notification(addresses, subject, message):
    """Send email notification."""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, addresses)
    except SMTPException:
        logger.error("SMTP error when sending notification.")
    except BadHeaderError:
        logger.error("Notification email contained invalid headers.")


def event_creation_notification(event):
    """Send notification when event is created."""
    addresses = getattr(settings, "EVENT_CREATION_NOTIFICATION_ADDRESSES", None)
    if addresses and event:
        subject = render_to_string(
            "notification/event_creation_subject.html", {"creator": event.organization.abbreviation}
        )
        message = render_to_string("notification/event_creation_message.html", {"event": event})
        send_notification(settings.EVENT_CREATION_NOTIFICATION_ADDRESSES, subject, message)


def competition_creation_notification(competition):
    """Send notification when competition is created."""
    addresses = getattr(settings, "COMPETITION_CREATION_NOTIFICATION_ADDRESSES", None)
    if_event_approved = getattr(settings, "COMPETITION_CREATION_NOTIFICATION_IF_EVENT_APPROVED", False)
    if addresses and competition and (not competition.event or if_event_approved or competition.event.approved):
        subject = render_to_string(
            "notification/competition_creation_subject.html", {"creator": competition.organization.abbreviation}
        )
        message = render_to_string("notification/competition_creation_message.html", {"competition": competition})
        send_notification(settings.COMPETITION_CREATION_NOTIFICATION_ADDRESSES, subject, message)

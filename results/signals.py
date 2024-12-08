from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from results.models.competitions import Competition
from results.models.events import Event
from results.models.organizations import Area, Organization
from results.models.results import Result, ResultPartial
from results.utils.notification import (
    competition_creation_notification,
    event_creation_notification,
)
from results.utils.records import check_records, check_records_partial


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Creates auth token when user is created."""
    if created and settings.CREATE_AUTH_TOKENS:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Result)
def check_result_records(sender, instance=None, created=False, **kwargs):
    """Check for records after result has been saved."""
    if instance:
        check_records(instance)


@receiver(post_save, sender=ResultPartial)
def check_result_records_partial(sender, instance=None, created=False, **kwargs):
    """Check for records after partial result has been saved."""
    if instance:
        check_records_partial(instance)


@receiver(post_save, sender=Organization)
def create_organization_group(sender, instance=None, created=False, **kwargs):
    """Creates group when organization is created."""
    group_name = "club_" + instance.abbreviation + "_" + str(instance.pk)
    if created and not instance.external and not instance.group and Group.objects.filter(name=group_name).count() == 0:
        group = Group.objects.create(name=group_name)
        instance.group = group
        instance.save()


@receiver(post_save, sender=Area)
def create_area_group(sender, instance=None, created=False, **kwargs):
    """Creates group when area is created."""
    group_name = "area_" + instance.abbreviation
    if created and not instance.group and Group.objects.filter(name=group_name).count() == 0:
        group = Group.objects.create(name=group_name)
        instance.group = group
        instance.save()


@receiver(post_save, sender=Competition)
def notify_competition_creation(sender, instance=None, created=False, **kwargs):
    """Notify when competition is created."""
    if created:
        competition_creation_notification(instance)


@receiver(post_save, sender=Event)
def notify_event_creation(sender, instance=None, created=False, **kwargs):
    """Notify when event is created."""
    if created:
        event_creation_notification(instance)

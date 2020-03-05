from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser

from results.mixins.change_log import LogChangesMixing


class Area(LogChangesMixing, models.Model):
    """Stores a single organizational area.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=100, unique=True, verbose_name=_('Abbreviation'))

    def __str__(self):
        return self.abbreviation

    class Meta:
        ordering = ['name']
        verbose_name = _('Area')
        verbose_name_plural = _('Areas')

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return False

    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False


class Organization(LogChangesMixing, models.Model):
    """Stores a single organization.

    Related to
     - :class:`django:django.contrib.auth.models.Group`
     - :class:`.organization.Area`
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=100, verbose_name=_('Abbreviation'))
    external = models.BooleanField(default=False, verbose_name=_('External'))
    areas = models.ManyToManyField(Area, blank=True, verbose_name=_('Areas'))
    group = models.OneToOneField(Group, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Group'))
    sport_id = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name=_('Sport ID'))
    historical = models.BooleanField(default=False, verbose_name=_('Historical'))

    def __str__(self):
        return '%s - %s' % (self.abbreviation, self.name)

    class Meta:
        ordering = ['name']
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        unique_together = ('name', 'abbreviation')

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return False

    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

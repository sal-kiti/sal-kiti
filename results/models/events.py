from django.db import models
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import authenticated_users

from results.mixins.change_log import LogChangesMixing
from results.models.organizations import Organization


class Event(LogChangesMixing, models.Model):
    """Stores a single event.

    Related to
    - :class:`.organization.Organization`
    """
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    date_start = models.DateField(verbose_name=_('Start date'))
    date_end = models.DateField(verbose_name=_('End date'))
    location = models.CharField(max_length=255, verbose_name=_('Location'))
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    locked = models.BooleanField(default=False, verbose_name=_('Edit lock'))
    public = models.BooleanField(default=False, verbose_name=_('Public'))

    def __str__(self):
        return '%s %s' % (self.date_start, self.name)

    class Meta:
        ordering = ['-date_start', 'name']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        return True

    @authenticated_users
    def has_object_write_permission(self, request):
        if (request.user.is_staff or request.user.is_superuser or
                self.organization.group in request.user.groups.all() and
                not self.locked):
            return True
        return False

    @authenticated_users
    def has_object_update_permission(self, request):
        if (request.user.is_staff or request.user.is_superuser or
                self.organization.group in request.user.groups.all() and
                not self.locked):
            return True
        return False

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser

from results.mixins.change_log import LogChangesMixing


class Sport(LogChangesMixing, models.Model):
    """Stores a single sport."""

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    abbreviation = models.CharField(max_length=15, verbose_name=_("Abbreviation"))
    suomisport_id = models.IntegerField(
        blank=True, null=True, unique=True, default=None, verbose_name=_("Suomisport ID")
    )
    order = models.SmallIntegerField(default=0, verbose_name=_("Order"))
    manager = models.OneToOneField(Group, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Manager"))

    historical = models.BooleanField(default=False, verbose_name=_("Historical"))

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ["order"]
        verbose_name = _("Sport")
        verbose_name_plural = _("Sports")

    def is_manager(self, user):
        """Check if user is sports manager

        :param user: user object
        :return: bool
        """
        groups = user.groups.all()
        try:
            Sport.objects.filter(manager__in=groups).get(pk=self.pk)
            return True
        except Sport.DoesNotExist:
            pass
        return False

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

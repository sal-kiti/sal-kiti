from django.db import models
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users


class StatisticsLink(models.Model):
    """Stores a single statistic link."""

    group = models.CharField(max_length=255, verbose_name=_("Group"))
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    link = models.TextField(verbose_name=_("Link"))
    highlight = models.SmallIntegerField(blank=True, null=True, verbose_name=_("Highlight"))
    public = models.BooleanField(default=True, verbose_name=_("Public"))
    order = models.SmallIntegerField(default=0, verbose_name=_("Order"))

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Statistics link")
        verbose_name_plural = _("Statistics links")

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

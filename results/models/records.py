from django.db import models
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser

from results.mixins.change_log import LogChangesMixing
from results.models.categories import Category
from results.models.competitions import CompetitionLevel, CompetitionType
from results.models.organizations import Area
from results.models.results import Result, ResultPartial


class RecordLevel(LogChangesMixing, models.Model):
    """Stores a single record level.

    Related to
     - :class:`.competitions.CompetitionLevel`
     - :class:`.results.Result`
    """
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=15, verbose_name=_('Abbreviation'))
    levels = models.ManyToManyField(CompetitionLevel)
    types = models.ManyToManyField(CompetitionType)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Area'))
    base = models.BooleanField(default=True, verbose_name=_('Base results'))
    partial = models.BooleanField(default=False, verbose_name=_('Partial results'))
    personal = models.BooleanField(default=True, verbose_name=_('Personal'))
    team = models.BooleanField(default=False, verbose_name=_('Team'))
    decimals = models.BooleanField(default=False, verbose_name=_('Decimals'))
    order = models.SmallIntegerField(default=0, verbose_name=_('Order'))
    historical = models.BooleanField(default=False, verbose_name=_('Historical'))

    def __str__(self):
        return '%s %s' % (self.abbreviation, self.name)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Record level')
        verbose_name_plural = _('Record levels')
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


class Record(LogChangesMixing, models.Model):
    """Stores a single record.

    Related to
     - :class:`.categories.Category`
     - :class:`.competitions.CompetitionType`
     - :class:`.results.Result`
    """
    result = models.ForeignKey(Result, related_name='record', on_delete=models.CASCADE)
    partial_result = models.ForeignKey(ResultPartial, null=True, blank=True, related_name='record_partial',
                                       on_delete=models.CASCADE)
    level = models.ForeignKey(RecordLevel, on_delete=models.CASCADE)
    type = models.ForeignKey(CompetitionType, related_name='record_type', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False, verbose_name=_('Approved'))
    date_start = models.DateField(verbose_name=_('Start date'))
    date_end = models.DateField(null=True, blank=True, verbose_name=_('End date'))
    info = models.TextField(blank=True, verbose_name=_('Info'))
    historical = models.BooleanField(default=False, verbose_name=_('Historical'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    def __str__(self):
        return '%s : %s : %s' % (self.level, self.type, self.category)

    def save(self, *args, **kwargs):
        """
        When saved, end approved and delete unapproved lower records.
        """
        super().save(*args, **kwargs)
        if self.approved and "approved" in self.changed_fields:
            if self.partial_result:
                records = Record.objects.filter(level=self.level, type=self.type, date_end=None, category=self.category,
                                                historical=False, partial_result__type=self.partial_result.type,
                                                partial_result__value__lt=self.partial_result.value)
            else:
                records = Record.objects.filter(level=self.level, type=self.type, date_end=None, category=self.category,
                                                historical=False, partial_result=None,
                                                result__result__lt=self.result.result)
            for record in records:
                if record.approved:
                    record.date_end = self.date_start
                    record.save()
                else:
                    record.delete()

    class Meta:
        ordering = ['type', 'result']
        verbose_name = _('Record')
        verbose_name_plural = _('Records')

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

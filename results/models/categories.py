from django.db import models
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser

from results.mixins.change_log import LogChangesMixing
from results.models.competitions import CompetitionType, CompetitionResultType
from results.models.sports import Sport


class Division(LogChangesMixing, models.Model):
    """Stores a single division."""
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=15, verbose_name=_('Abbreviation'))
    historical = models.BooleanField(default=False, verbose_name=_('Historical'))

    def __str__(self):
        return '%s - %s' % (self.abbreviation, self.name)

    class Meta:
        ordering = ['name']
        verbose_name = _('Division')
        verbose_name_plural = _('Division')

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


class Category(LogChangesMixing, models.Model):
    """Stores a single category.

    Related to
     - :class:`.categories.Division`
     - :class:`.categories.Sport`

    Defined values for a gender are M (Man), W (Woman), O (Other/Unknown).
    """
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=15, verbose_name=_('Abbreviation'))
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True)
    max_age = models.SmallIntegerField(null=True, blank=True, verbose_name=_('Maximum age'))
    min_age = models.SmallIntegerField(null=True, blank=True, verbose_name=_('Minimum age'))
    age_exact = models.BooleanField(default=False, verbose_name=_('Age limit checked by the exact day, not year'))
    team = models.BooleanField(default=False, verbose_name=_('Team category'))
    team_size = models.SmallIntegerField(null=True, blank=True, verbose_name=_('Number of team members'))
    GENDER_CHOICES = (
        ('M', _('Man')),
        ('W', _('Woman')),
        ('O', _('Other')),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name=_('Gender'))
    order = models.SmallIntegerField(default=0, verbose_name=_('Order'))
    historical = models.BooleanField(default=False, verbose_name=_('Historical'))

    def __str__(self):
        return '%s: %s - %s' % (self.sport, self.abbreviation, self.name)

    class Meta:
        ordering = ['sport', 'order', 'team', 'name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

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


class CategoryForCompetitionType(LogChangesMixing, models.Model):
    """Stores a single competition type and category validation check.

    Related to
     - :class:`.categories.Category`
     - :class:`.competitions.CompetitionType`
     """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.ForeignKey(CompetitionType, on_delete=models.CASCADE)
    max_result = models.SmallIntegerField(blank=True, null=True, verbose_name=_('Maximum result'))
    min_result = models.SmallIntegerField(blank=True, null=True, verbose_name=_('Minimum result'))
    disallow = models.BooleanField(default=False, verbose_name=_('Disallow category for this competition type'))
    check_record = models.BooleanField(default=True, verbose_name=_('Check records'))
    check_record_partial = models.BooleanField(default=True, verbose_name=_('Check partial records'))
    record_group = models.SmallIntegerField(blank=True, null=True, verbose_name=_('Record group'))
    limit_partial = models.ManyToManyField(CompetitionResultType, blank=True,
                                           verbose_name=_('No partial records for listed result types'))

    def __str__(self):
        return '%s %s' % (self.type, self.category)

    class Meta:
        ordering = ['type', 'category']
        verbose_name = _('Competition type and category check')
        verbose_name_plural = _('Competition type and category checks')

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

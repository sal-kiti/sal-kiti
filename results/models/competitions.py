from django.db import models
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users

from results.mixins.change_log import LogChangesMixing
from results.models.events import Event
from results.models.organizations import Organization
from results.models.sports import Sport


class CompetitionLayout(LogChangesMixing, models.Model):
    """Stores a single competition layout.

    Related to
     - :class:`.competitions.CompetitionType`
     """
    SIZE_CHOICES = [
        ('sm', 'Small'),
        ('md', 'Medium'),
        ('lg', 'Large'),
        ('xl', 'Extra large')
    ]
    type = models.SmallIntegerField(verbose_name=_('Layout type'))
    label = models.CharField(max_length=100, verbose_name=_('Label'))
    name = models.CharField(max_length=15, verbose_name=_('Result type name'))
    block = models.SmallIntegerField(verbose_name=_('Block'))
    row = models.SmallIntegerField(verbose_name=_('Row'))
    col = models.SmallIntegerField(verbose_name=_('Column'))
    order = models.SmallIntegerField(null=True, blank=True, verbose_name=_('Order'))
    hide = models.CharField(max_length=3, choices=SIZE_CHOICES, blank=True, verbose_name=_('Hide on smaller screen'))
    show = models.CharField(max_length=3, choices=SIZE_CHOICES, blank=True, verbose_name=_('Show on larger screen'))

    def __str__(self):
        return '%s %s %s' % (self.type, self.label, self.name)

    class Meta:
        ordering = ['type', 'block', 'row', 'col', 'order']
        verbose_name = _('Competition layout')
        verbose_name_plural = _('Competition layouts')
        unique_together = ('type', 'block', 'row', 'col')

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


class CompetitionLevel(LogChangesMixing, models.Model):
    """Stores a single competition level."""
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=15, unique=True, verbose_name=_('Abbreviation'))
    order = models.SmallIntegerField(default=0, verbose_name=_('Order'))
    requirements = models.CharField(blank=True, max_length=100, verbose_name=_('Requirements'))
    area_competition = models.BooleanField(default=False, verbose_name=_('Area competition'))
    require_approval = models.BooleanField(default=False, verbose_name=_('Require approved competition to add results'))
    historical = models.BooleanField(default=False, verbose_name=_('Historical'))

    def __str__(self):
        return '%s %s' % (self.abbreviation, self.name)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Competition level')
        verbose_name_plural = _('Competition levels')

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


class CompetitionType(LogChangesMixing, models.Model):
    """Stores a single competition type.

    Related to
     - :class:`.categories.Sport`
     """
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=15, verbose_name=_('Abbreviation'))
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_rounds = models.SmallIntegerField(verbose_name=_('Number of rounds'))
    max_result = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3,
                                     verbose_name=_('Maximum result'))
    min_result = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3,
                                     verbose_name=_('Minimum result'))
    order = models.SmallIntegerField(default=0, verbose_name=_('Order'))
    requirements = models.CharField(blank=True, max_length=100, verbose_name=_('Requirements'))
    personal = models.BooleanField(default=True, verbose_name=_('Personal competition'))
    team = models.BooleanField(default=True, verbose_name=_('Team competition'))
    layout = models.SmallIntegerField(default=1, verbose_name=_('Layout type'))
    historical = models.BooleanField(default=False, verbose_name=_('Historical'))

    def __str__(self):
        return '%s : %s %s' % (self.sport, self.abbreviation, self.name)

    class Meta:
        ordering = ['sport', 'order', 'name']
        verbose_name = _('Competition type')
        verbose_name_plural = _('Competition types')

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


class CompetitionResultType(LogChangesMixing, models.Model):
    """Stores a single result type.

    Related to
     - :class:`.competitions.CompetitionType`
    """
    competition_type = models.ForeignKey(CompetitionType, related_name='competition_type', on_delete=models.CASCADE)
    name = models.CharField(max_length=15, verbose_name=_('Name'))
    abbreviation = models.CharField(max_length=10, verbose_name=_('Abbreviation'))
    max_result = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3,
                                     verbose_name=_('Maximum result'))
    min_result = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=3,
                                     verbose_name=_('Minimum result'))
    records = models.BooleanField(default=True, verbose_name=_('Check records'))

    def __str__(self):
        return '%s %s' % (self.competition_type, self.abbreviation)

    class Meta:
        ordering = ['competition_type', 'name']
        verbose_name = _('Result type')
        verbose_name_plural = _('Result types')

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


class Competition(LogChangesMixing, models.Model):
    """Stores a single competition.

    Related to
     - :class:`.events.Event`
     - :class:`.organizations.Organization`
     - :class:`.competitions.CompetitionLevel`
     - :class:`.competitions.CompetitionType`
    """
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    date_start = models.DateField(verbose_name=_('Start date'))
    date_end = models.DateField(verbose_name=_('End date'))
    location = models.CharField(max_length=255, verbose_name=_('Location'))
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, related_name='competitions', null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey(CompetitionType, on_delete=models.CASCADE)
    level = models.ForeignKey(CompetitionLevel, on_delete=models.CASCADE)
    layout = models.SmallIntegerField(default=1, verbose_name=_('Layout type'))
    approved = models.BooleanField(default=False, verbose_name=_('Approved'))
    locked = models.BooleanField(default=False, verbose_name=_('Edit lock'))
    public = models.BooleanField(default=False, verbose_name=_('Public'))
    trial = models.BooleanField(default=False, verbose_name=_('Trial competition'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    def __str__(self):
        return '%s %s' % (self.date_start, self.name)

    def date(self):
        if self.date_start != self.date_end:
            return '%s - %s' % (self.date_start, self.date_end)
        else:
            return '%s' % self.date_start

    class Meta:
        ordering = ['-date_start', 'name']
        verbose_name = _('Competition')
        verbose_name_plural = _('Competitions')

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
        if ((request.user.is_staff or request.user.is_superuser) or
                (self.organization.is_area_manager(request.user)
                 and self.event.organization.is_area_manager(request.user)) or
                (self.organization.is_manager(request.user) and self.event.organization.is_manager(request.user) and
                    not self.locked and not self.event.locked)):
            return True
        return False

    @authenticated_users
    def has_object_update_permission(self, request):
        if ((request.user.is_staff or request.user.is_superuser) or
                self.organization.is_area_manager(request.user) or
                (self.organization.is_manager(request.user) and
                    not self.locked and not self.event.locked)):
            return True
        return False

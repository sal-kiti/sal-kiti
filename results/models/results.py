from django.db import models
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import authenticated_users

from results.mixins.change_log import LogChangesMixing
from results.models.athletes import Athlete
from results.models.categories import Category
from results.models.competitions import Competition, CompetitionResultType
from results.models.organizations import Organization


class Result(LogChangesMixing, models.Model):
    """Stores a single result.

    Related to
     - :class:`.athletes.Athlete`
     - :class:`.categories.Category`
     - :class:`.competitions.Competition`
     - :class:`.organizations.Organization`
    """
    competition = models.ForeignKey(Competition, related_name='results_competition', on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, related_name='results_athlete', null=True, blank=True,
                                on_delete=models.CASCADE)
    team_members = models.ManyToManyField(Athlete, blank=True, related_name='team_members')
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('First name'))
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Last name'))
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    elimination_category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True, related_name='eliminiation_category')
    result = models.DecimalField(blank=True, null=True, verbose_name=_('Result'), max_digits=12, decimal_places=3)
    result_code = models.CharField(blank=True, max_length=3, verbose_name=_('Result code'))
    decimals = models.SmallIntegerField(default=0, verbose_name=_('Result decimals'))
    position = models.SmallIntegerField(null=True, blank=True, verbose_name=_('Position'))
    position_pre = models.SmallIntegerField(null=True, blank=True, verbose_name=_('Preliminary position'))
    approved = models.BooleanField(default=False, verbose_name=_('Approved'))
    info = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Additional information'))
    admin_info = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Administrational information'))
    team = models.BooleanField(default=False, verbose_name=_('Team result'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    def __str__(self):
        return '%s %s %s' % (self.competition, self.last_name, self.first_name)

    def save(self, *args, **kwargs):
        """
        Add result names from the athlete if not included.
        Set position_pre as position if not included and vice versa.
        """
        if self.athlete:
            if not self.first_name:
                self.first_name = self.athlete.first_name
            if not self.last_name:
                self.last_name = self.athlete.last_name
        if not self.position_pre and self.position:
            self.position_pre = self.position
        elif not self.position and self.position_pre:
            self.position = self.position_pre
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['competition', 'category', 'position', '-result']
        verbose_name = _('Result')
        verbose_name_plural = _('Results')

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
    def has_object_update_permission(self, request):
        if (request.user.is_staff or request.user.is_superuser or
                (self.competition.organization.group in request.user.groups.all() and
                 not (self.competition.locked or self.approved))):
            return True
        return False

    @authenticated_users
    def has_object_write_permission(self, request):
        if (request.user.is_staff or request.user.is_superuser or
                (self.competition.organization.group in request.user.groups.all() and
                 not (self.competition.locked or self.approved))):
            return True
        return False


class ResultPartial(LogChangesMixing, models.Model):
    """Stores a single partial result.

    Related to
     - :class:`.competitions.CompetitionResultType`
     - :class:`.results.Result`
    """
    result = models.ForeignKey(Result, related_name='partial', on_delete=models.CASCADE)
    type = models.ForeignKey(CompetitionResultType, related_name='result_type', on_delete=models.CASCADE)
    order = models.SmallIntegerField(verbose_name=_('Order'))
    value = models.DecimalField(blank=True, null=True, verbose_name=_('Value'), max_digits=12, decimal_places=3)
    code = models.CharField(blank=True, max_length=3, verbose_name=_('Code'))
    decimals = models.SmallIntegerField(default=0, verbose_name=_('Value decimals'))
    time = models.TimeField(null=True, blank=True, verbose_name=_('Time'))
    text = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Text value'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    def __str__(self):
        return '%s : %s %s' % (self.result, self.type, self.order)

    class Meta:
        ordering = ['result', 'type', 'order']
        verbose_name = _('Partial result')
        verbose_name_plural = _('Partial results')
        indexes = [
            models.Index(fields=['result', 'type', 'order']),
        ]
        unique_together = ('result', 'type', 'order')

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
    def has_object_update_permission(self, request):
        if (request.user.is_staff or request.user.is_superuser or
                (self.result.competition.organization.group in request.user.groups.all() and
                 not (self.result.competition.locked or self.result.approved))):
            return True
        return False

    @authenticated_users
    def has_object_write_permission(self, request):
        if (request.user.is_staff or request.user.is_superuser or
                (self.result.competition.organization.group in request.user.groups.all() and
                 not (self.result.competition.locked or self.result.approved))):
            return True
        return False

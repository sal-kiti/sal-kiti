from django.core.validators import RegexValidator
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
    approved = models.BooleanField(default=False, verbose_name=_('Approved'))
    locked = models.BooleanField(default=False, verbose_name=_('Edit lock'))
    public = models.BooleanField(default=False, verbose_name=_('Public'))
    categories = models.TextField(blank=True, verbose_name=_('Competition categories'))
    optional_dates = models.TextField(blank=True, verbose_name=_('Optional dates'))
    web_page = models.URLField(blank=True, verbose_name=_('Web page'))
    invitation = models.URLField(blank=True, verbose_name=_('Invitation URL'))
    notes = models.TextField(blank=True, verbose_name=_('Generic notes'))
    safety_plan = models.BooleanField(default=False, verbose_name=_('Safety plan exists'))
    international = models.BooleanField(default=False, verbose_name=_('International competition'))
    toc_agreement = models.BooleanField(default=False, verbose_name=_('Terms and Conditions agreement'))

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


class EventContact(LogChangesMixing, models.Model):
    """Stores a single contact for the event.

    Related to
    - :class:`.events.EventRegistration`
    """
    TYPE_CHOICES = [
        ('contact', _('Generic contact')),
        ('manager', _('Competition manager')),
        ('head judge', _('Head judge')),
        ('technical', _('Technical manager'))
    ]
    phone_regex = RegexValidator(regex=r'^\+?1?\d{7,15}$',
                                 message=_('Phone number may start with "+" and only contain digits.'))

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name=_('Contact type'))
    first_name = models.CharField(max_length=100, verbose_name=_('First name'))
    last_name = models.CharField(max_length=100, verbose_name=_('Last name'))
    email = models.EmailField(blank=True, verbose_name=_('Email address'))
    phone = models.CharField(max_length=17, validators=[phone_regex], blank=True, verbose_name=_('Phone number'))

    def __str__(self):
        return '%s: %s %s' % (self.type, self.first_name, self.last_name)

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
                self.event.organization.group in request.user.groups.all() and
                not self.event.locked):
            return True
        return False

    @authenticated_users
    def has_object_update_permission(self, request):
        if (request.user.is_staff or request.user.is_superuser or
                self.event.organization.group in request.user.groups.all() and
                not self.event.locked):
            return True
        return False

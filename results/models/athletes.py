from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users

from results.mixins.change_log import LogChangesMixing
from results.models.organizations import Organization
from results.models.sports import Sport


class Athlete(LogChangesMixing, models.Model):
    """Stores a single athlete.

    Related to
      - :class:`.organizations.Organization`

    Gender and date of birth are used for the result validation.
    """

    GENDER_CHOICES = (
        ("M", _("Man")),
        ("W", _("Woman")),
        ("O", _("Other")),
        ("U", _("Unknown")),
    )
    first_name = models.CharField(max_length=100, verbose_name=_("First name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last name"))
    sport_id = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name=_("Sport ID"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of birth"))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_("Gender"))
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    additional_organizations = models.ManyToManyField(
        Organization, blank=True, related_name="additional_organizations"
    )
    no_auto_update = models.BooleanField(default=False, verbose_name=_("No automatic updates"))

    class Meta:
        ordering = ["last_name", "first_name", "sport_id"]
        verbose_name = _("Athlete")
        verbose_name_plural = _("Athletes")

    def __str__(self):
        return "%s %s, %s" % (self.first_name, self.last_name, self.organization)

    @staticmethod
    @allow_staff_or_superuser
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
    @authenticated_users
    def has_create_permission(request):
        return True


class AthleteInformation(LogChangesMixing, models.Model):
    """Stores a single athlete specific information.

    Related to
      - :class:`.athletes.Athlete`
    """

    VISIBILITY_CHOICES = (
        ("P", _("Public")),
        ("A", _("Authenticated users")),
        ("S", _("Staff users")),
        ("U", _("Superuser only")),
    )
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="info")
    sport = models.ForeignKey(
        Sport, on_delete=models.CASCADE, blank=True, null=True, default=None, related_name="athlete_info"
    )
    type = models.CharField(max_length=100, verbose_name=_("Type"))
    suomisport_id = models.IntegerField(blank=True, null=True, default=None, verbose_name=_("Suomisport ID"))
    value = models.CharField(max_length=100, verbose_name=_("Value"))
    date_start = models.DateField(blank=True, null=True, verbose_name=_("Start date"))
    date_end = models.DateField(blank=True, null=True, verbose_name=_("End date"))
    visibility = models.CharField(max_length=1, choices=VISIBILITY_CHOICES, default="P", verbose_name=_("Visibility"))
    modification_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Suomisport update timestamp"))

    def __str__(self):
        return "%s, %s" % (self.athlete, self.type)

    @staticmethod
    def get_visibility(user):
        """
        Returns the list of allowed visibility for user

        :param user:
        :return: list
        """
        if not user or not user.is_authenticated:
            return ["P"]
        elif user.is_superuser:
            return ["P", "A", "S", "U"]
        elif user.is_staff:
            return ["P", "A", "S"]
        else:
            return ["P", "A"]

    @staticmethod
    def get_visibility_queryset(user, queryset):
        """
        Returns the queryset of athlete information allowed for user

        :param user:
        :param queryset:
        :return: queryset
        """
        if not user or not user.is_authenticated:
            return queryset.filter(visibility__in=["P"], date_start__lte=date.today(), date_end__gte=date.today())
        elif user.is_superuser:
            return queryset.filter(visibility__in=["P", "A", "S", "U"])
        elif user.is_staff:
            return queryset.filter(visibility__in=["P", "A", "S"])
        else:
            return queryset.filter(visibility__in=["P", "A"], date_start__lte=date.today(), date_end__gte=date.today())

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        if self.visibility == "P":
            return True
        elif request.user.is_authenticated and self.visibility == "A":
            return True
        elif (request.user.is_staff or request.user.is_superuser) and self.visibility == "S":
            return True
        elif request.user.is_superuser and self.visibility == "U":
            return True
        return False

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

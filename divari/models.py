from django.db import models
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users

from results.models.organizations import Organization


class Competition(models.Model):
    """Stores a single competition."""

    organization = models.ForeignKey(Organization, related_name="divari_competition", on_delete=models.CASCADE)
    date = models.DateField(_("Date"))

    def __str__(self):
        return "%s, %s" % (self.organization, self.date)

    class Meta:
        verbose_name = _("Competition")
        verbose_name_plural = _("Competitions")

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
        return True

    @authenticated_users
    def has_object_update_permission(self, request):
        return False

    @staticmethod
    @authenticated_users
    def has_create_permission(request):
        return True


class Season(models.Model):
    """Stores a single season."""

    name = models.CharField(_("Season name"), max_length=40)
    date_start = models.DateField(_("Start date"))
    date_end = models.DateField(_("End date"))
    result_count = models.SmallIntegerField(_("Number of included results"), default=1)
    start_level_recurve = models.SmallIntegerField(_("Recurve start level"), default=1)
    start_level_compound = models.SmallIntegerField(_("Compound start level"), default=1)
    start_level_barebow = models.SmallIntegerField(_("Barebow start level"), default=1)
    start_level_longbow = models.SmallIntegerField(_("Longbow start level"), default=1)
    start_level_junrecurve = models.SmallIntegerField(_("Junior Recurve start level"), default=1)
    start_level_juncompound = models.SmallIntegerField(_("Junior Compound start level"), default=1)
    start_level_junbarebow = models.SmallIntegerField(_("Junior Barebow start level"), default=1)

    def __str__(self):
        return "%s, %s - %s" % (self.name, self.date_start, self.date_end)

    class Meta:
        verbose_name = _("Season")
        verbose_name_plural = _("Seasons")

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


class Team(models.Model):
    """Stores a single team."""

    BOW_TYPE_CHOICES = (
        ("recurve", _("Recurve")),
        ("compound", _("Compound")),
        ("barebow", _("Barebow")),
        ("longbow", _("Longbow")),
        ("junrecurve", _("Junior Recurve")),
        ("juncompound", _("Junior Compound")),
        ("junbarebow", _("Junior Barebow")),
    )
    bow_type = models.CharField(_("Bow type"), max_length=11, choices=BOW_TYPE_CHOICES, default="recurve")
    organization = models.ForeignKey(Organization, related_name="divari_team", on_delete=models.CASCADE)
    number = models.SmallIntegerField(_("Number"))
    division = models.SmallIntegerField(_("Division"))
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    def __str__(self):
        return "%s: %s %s %s" % (self.season, self.organization, self.bow_type, self.number)

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

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


class TeamResult(models.Model):
    """Stores a single team result."""

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    result = models.SmallIntegerField(_("Result"))

    def __str__(self):
        return "%s, %s" % (self.competition, self.team)

    class Meta:
        verbose_name = _("Team result")
        verbose_name_plural = _("Team results")


class SeasonResult(models.Model):
    """Stores a single season result."""

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    result = models.SmallIntegerField(_("result"))

    def __str__(self):
        return "%s" % (self.team)

    class Meta:
        verbose_name = _("Season result")
        verbose_name_plural = _("Season results")
        ordering = ["team__bow_type", "team__division", "-result"]

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


class Result(models.Model):
    """Stores a single result."""

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    BOW_TYPE_CHOICES = (
        ("recurve", _("Recurve")),
        ("compound", _("Compound")),
        ("barebow", _("Barebow")),
        ("longbow", _("Longbow")),
        ("junrecurve", _("Junior Recurve")),
        ("juncompound", _("Junior Compound")),
        ("junbarebow", _("Junior Barebow")),
    )
    bow_type = models.CharField(_("Bow type"), max_length=11, choices=BOW_TYPE_CHOICES, default="recurve")
    TARGET_CHOICES = (("40", "40 cm"), ("60", "60 cm"), ("80", "80 cm"), ("122", "122 cm"))
    target_type = models.CharField(_("Target type"), max_length=3, choices=TARGET_CHOICES, default="40")
    athlete = models.CharField(_("Athlete"), max_length=50)
    result = models.SmallIntegerField(_("result"))

    def __str__(self):
        return "%s, %s" % (self.competition, self.athlete)

    class Meta:
        verbose_name = _("Result")
        verbose_name_plural = _("Results")

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
        return True

    @authenticated_users
    def has_object_update_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):
        return True

import calendar
import datetime

from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from divari.models import Competition, Result, Season, SeasonResult, Team
from results.models.organizations import Organization


class CompetitionSerializer(serializers.ModelSerializer):
    """
    Serializer for divari competitions
    """

    organization = serializers.SlugRelatedField(queryset=Organization.objects.all(), slug_field="name")

    permissions = DRYPermissionsField()

    class Meta:
        model = Competition
        fields = ("id", "organization", "date", "permissions")
        ref_name = "DivariCompetitionSerializer"

    def validate(self, data):
        """
        Checks permissions to create or modify competitions.

        Users may create one competition per month
        """
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError(_("User not authenticated"), 403)
        date = data["date"]
        date_start = date.replace(day=1)
        date_end = date.replace(day=calendar.monthrange(date.year, date.month)[1])
        if Season.objects.filter(date_start__lte=date, date_end__gte=date).count() == 0:
            raise serializers.ValidationError(_("There is no Divari season active."))
        if not user.is_superuser and not user.is_staff:
            if "organization" not in data or data["organization"].group not in user.groups.all():
                raise serializers.ValidationError(_("No permission to alter or create an competition."), 403)
            if date < datetime.date.today() - datetime.timedelta(days=31):
                raise serializers.ValidationError(_("Cannot create a competition more than one month in past."))
        if date > datetime.date.today():
            raise serializers.ValidationError(_("Cannot create a future competition."))
        if (
            Competition.objects.filter(
                organization=data["organization"], date__gte=date_start, date__lte=date_end
            ).count()
            > 1
        ):
            raise serializers.ValidationError(_("There is already two competitions in this month."))
        return data


class ResultSerializer(serializers.ModelSerializer):
    """
    Serializer for divari results
    """

    permissions = DRYPermissionsField()

    class Meta:
        model = Result
        fields = ("id", "competition", "bow_type", "target_type", "athlete", "result", "permissions")
        validators = [
            UniqueTogetherValidator(
                queryset=Result.objects.all(), fields=["competition", "bow_type", "target_type", "athlete"]
            )
        ]
        ref_name = "DivariResultSerializer"

    def validate_result(self, value):
        if value < 0 or value > 720:
            raise serializers.ValidationError(_("Invalid result value"))
        return value

    def validate(self, data):
        """
        Checks permissions to create or modify competitions.

        Users may create one competition per month
        """
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError(_("User not authenticated"), 403)
        if not user.is_superuser and not user.is_staff:
            if "competition" not in data or data["competition"].organization.group not in user.groups.all():
                raise serializers.ValidationError(_("No permission to create a result for this competition."), 403)
            if data["competition"].date < datetime.date.today() - datetime.timedelta(days=31):
                raise serializers.ValidationError(_("Cannot create a result more than one month in past."))
        return data


class SeasonSerializer(serializers.ModelSerializer):
    """
    Serializer for divari seasons
    """

    permissions = DRYPermissionsField()

    class Meta:
        model = Season
        fields = (
            "id",
            "name",
            "date_start",
            "date_end",
            "result_count",
            "start_level_recurve",
            "start_level_compound",
            "start_level_barebow",
            "permissions",
        )
        ref_name = "DivariSeasonSerializer"


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for divari teams
    """

    organization = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Team
        fields = ("id", "bow_type", "organization", "number", "division", "season")
        ref_name = "DivariTeamSerializer"


class SeasonResultSerializer(serializers.ModelSerializer):
    """
    Serializer for divari seasons
    """

    team = TeamSerializer()

    class Meta:
        model = SeasonResult
        fields = ("id", "team", "result")
        ref_name = "DivariSeasonResultSerializer"

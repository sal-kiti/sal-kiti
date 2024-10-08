from django.conf import settings
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.mixins.eager_loading import EagerLoadingMixin
from results.models.athletes import Athlete, AthleteInformation
from results.models.organizations import Organization
from results.models.sports import Sport
from results.serializers.organizations import OrganizationSerializer


class AthleteInformationSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for athletes additional information.
    """

    sport = serializers.SlugRelatedField(slug_field="name", queryset=Sport.objects.all(), allow_null=True)

    permissions = DRYPermissionsField()

    class Meta:
        model = AthleteInformation
        fields = ("id", "athlete", "sport", "type", "value", "date_start", "date_end", "visibility", "permissions")


class AthleteSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for athletes.
    """

    organization_info = OrganizationSerializer(read_only=True, source="organization")
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    info = AthleteInformationSerializer(many=True, read_only=True)

    permissions = DRYPermissionsField()

    _PREFETCH_RELATED_FIELDS = [
        "info__sport",
        "organization",
        "organization__areas",
        "additional_organizations",
    ]

    class Meta:
        model = Athlete
        fields = (
            "id",
            "first_name",
            "last_name",
            "sport_id",
            "organization",
            "organization_info",
            "additional_organizations",
            "date_of_birth",
            "gender",
            "info",
            "permissions",
        )

    def to_representation(self, instance):
        """
        Hide gender and date_of_birth unless POST or user is in UNMASKED_ATHLETE_USERS settings list.
        """
        data = super().to_representation(instance)
        if (
            "request" in self.context
            and self.context["request"].method != "POST"
            and (self.context["request"].user.username not in getattr(settings, "UNMASKED_ATHLETE_USERS", []))
        ):
            for field in ["date_of_birth", "gender"]:
                data.pop(field, None)
        return data

    def validate(self, data):
        """
        Check permissions to create an athlete.

        External organization athletes may be created by any logged in user.
        """
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError(_("User not authenticated"), 403)
        if user.is_superuser or user.is_staff:
            return data
        if "organization" not in data or not data["organization"].external:
            raise serializers.ValidationError(_("No permission to create non external athlete"), 403)
        return data


class AthleteLimitedSerializer(AthleteSerializer):
    """
    Serializer for athletes to users without staff permissions
    """

    organization_info = OrganizationSerializer(read_only=True, source="organization")
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    info = AthleteInformationSerializer(many=True, read_only=True)

    class Meta:
        model = Athlete
        fields = (
            "id",
            "first_name",
            "last_name",
            "sport_id",
            "organization",
            "organization_info",
            "additional_organizations",
            "info",
        )


class AthleteNameSerializer(AthleteSerializer):
    """
    Serializer for athlete name and sport ID
    """

    class Meta:
        model = Athlete
        fields = ("id", "first_name", "last_name", "sport_id")

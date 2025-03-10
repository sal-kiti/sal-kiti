from django.conf import settings
from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers, status

from results.mixins.eager_loading import EagerLoadingMixin
from results.models.competitions import Competition
from results.models.events import Event, EventContact
from results.models.organizations import Organization
from results.serializers.athletes import AthleteLimitedSerializer
from results.serializers.organizations import OrganizationSerializer
from results.utils.custom_validation import CustomValidation


class CompetitionInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for competition info in events
    """

    type = serializers.SlugRelatedField(read_only=True, slug_field="name")
    level = serializers.SlugRelatedField(read_only=True, slug_field="name")
    sport = serializers.PrimaryKeyRelatedField(read_only=True, source="type.sport")

    class Meta:
        model = Competition
        fields = ("id", "type", "sport", "level", "public")


class EventSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for events
    """

    organization_info = OrganizationSerializer(read_only=True, source="organization")
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    competitions = CompetitionInfoSerializer(many=True, read_only=True)
    permissions = DRYPermissionsField()

    _PREFETCH_RELATED_FIELDS = [
        "organization",
        "organization__areas",
        "competitions",
        "competitions__level",
        "competitions__type",
        "competitions__type__sport",
    ]

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "description",
            "date_start",
            "date_end",
            "location",
            "organization",
            "organization_info",
            "public",
            "competitions",
            "locked",
            "approved",
            "permissions",
            "categories",
            "optional_dates",
            "web_page",
            "invitation",
            "notes",
            "international",
            "safety_plan",
            "toc_agreement",
        )

    def is_sport_manager(self, user, event):
        """
        Check if the user is a sport manager for any of the competition sports in the event.
        """
        for competition in event.competitions.all():
            if competition.type.sport.is_manager(user):
                return True
        return False

    def to_representation(self, instance):
        """
        Hide some fields if user is not organizers representative, staff or superuser
        """
        data = super().to_representation(instance)
        user = self.context["request"].user
        if not user.is_authenticated or (
            not user.is_superuser
            and not user.is_staff
            and not instance.organization.is_manager(user)
            and not instance.organization.is_area_manager(user)
            and not self.is_sport_manager(user, instance)
        ):
            for field in ["locked", "optional_dates", "notes", "safety_plan", "international", "toc_agreement"]:
                data.pop(field, None)
        return data

    @staticmethod
    def validate_toc_agreement(value):
        if not value:
            raise serializers.ValidationError(_("Must agree to the terms and conditions."), 403)
        return value

    def validate(self, data):
        """
        Checks permissions to create or modify events.

        Users may create and modify events organized by the clubs they
        represent, unless the event is locked by the staff.
        """
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError(_("User not authenticated"), 403)
        if "date_end" in data and "date_start" in data and data["date_end"] < data["date_start"]:
            raise serializers.ValidationError(_("Start date may not be later than End date."))
        if (
            user.is_superuser
            or user.is_staff
            or (
                (not self.instance or self.instance.organization.is_area_manager(user))
                and ("organization" not in data or data["organization"].is_area_manager(user))
            )
        ):
            return data
        if self.instance:
            for competition in self.instance.competitions.all():
                if competition.type.sport.is_manager(user):
                    return data
        if not (self.instance and self.instance.organization.group in user.groups.all()) and (
            "organization" not in data or data["organization"].group not in user.groups.all()
        ):
            raise serializers.ValidationError(_("No permission to alter or create an event."), 403)
        if (self.instance and self.instance.locked) or ("locked" in data and data["locked"]):
            raise serializers.ValidationError(_("No permission to alter or create a locked event."), 403)
        if settings.EVENT_PUBLISH_REQUIRES_STAFF and (
            (not self.instance or not self.instance.public) and "public" in data and data["public"]
        ):
            raise CustomValidation(_("No permission to publish event."), "publish", status.HTTP_403_FORBIDDEN)
        if (not self.instance or not self.instance.approved) and "approved" in data and data["approved"]:
            raise CustomValidation(_("No permission to approve event."), "approved", status.HTTP_403_FORBIDDEN)
        return data


class EventLimitedSerializer(EventSerializer):
    """
    Limited info serializer for events
    """

    class Meta:
        model = Event
        fields = ("id", "name", "description", "date_start", "date_end")


class EventContactSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for event contacts
    """

    athlete_info = AthleteLimitedSerializer(read_only=True, source="athlete")
    event_info = EventLimitedSerializer(read_only=True, source="event")

    _PREFETCH_RELATED_FIELDS = [
        "athlete",
        "athlete__additional_organizations",
        "athlete__info__sport",
        "athlete__organization",
        "athlete__organization__areas",
        "event",
    ]

    class Meta:
        model = EventContact
        fields = (
            "id",
            "event",
            "event_info",
            "type",
            "athlete",
            "athlete_info",
            "first_name",
            "last_name",
            "email",
            "phone",
        )
        extra_kwargs = {"email": {"required": False}, "phone": {"required": False}}

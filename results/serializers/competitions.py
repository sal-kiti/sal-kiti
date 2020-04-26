from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.mixins.eager_loading import EagerLoadingMixin
from results.models.competitions import Competition, CompetitionLevel, CompetitionResultType, CompetitionType
from results.models.competitions import CompetitionLayout
from results.models.events import Event
from results.models.organizations import Organization
from results.serializers.events import EventLimitedSerializer
from results.serializers.organizations import OrganizationSerializer


class CompetitionLevelSerializer(serializers.ModelSerializer):
    """
    Serializer for competition levels
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = CompetitionLevel
        fields = (
            'id', 'name', 'abbreviation', 'historical', 'order', 'requirements', 'permissions')


class CompetitionTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for competition types
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = CompetitionType
        fields = (
            'id', 'name', 'abbreviation', 'number_of_rounds', 'max_result', 'min_result', 'sport', 'personal', 'team',
            'layout', 'requirements', 'historical', 'permissions')


class CompetitionLayoutSerializer(serializers.ModelSerializer):
    """
    Serializer for competition layouts
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = CompetitionLayout
        fields = (
            'id', 'type', 'label', 'name', 'block', 'row', 'col', 'order', 'hide', 'show',
            'permissions')


class CompetitionResultTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for competition result types
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = CompetitionResultType
        fields = (
            'id', 'competition_type', 'name', 'abbreviation', 'max_result', 'min_result', 'permissions')


class CompetitionResultTypeLimitedSerializer(serializers.ModelSerializer):
    """
    Limited serializer for competition result types
    """

    class Meta:
        model = CompetitionResultType
        fields = (
            'id', 'name', 'abbreviation')


class CompetitionSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for competitions
    """
    type_info = CompetitionTypeSerializer(read_only=True, source='type')
    type = serializers.PrimaryKeyRelatedField(
        queryset=CompetitionType.objects.all())
    level_info = CompetitionLevelSerializer(read_only=True, source='level')
    level = serializers.PrimaryKeyRelatedField(
        queryset=CompetitionLevel.objects.all())
    organization_info = OrganizationSerializer(read_only=True, source='organization')
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all())
    event_info = EventLimitedSerializer(read_only=True, source='event')
    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all())

    permissions = DRYPermissionsField()

    _PREFETCH_RELATED_FIELDS = ['type',
                                'level',
                                'event',
                                'event__organization__areas',
                                'organization',
                                'organization__areas']

    class Meta:
        model = Competition
        fields = (
            'id', 'name', 'description', 'date_start', 'date_end', 'location', 'organization', 'organization_info',
            'event', 'event_info', 'type', 'type_info', 'level', 'level_info', 'layout', 'locked', 'public',
            'trial', 'permissions')

    def validate(self, data):
        """
        Checks permissions to create or modify competitions.

        Users may create and modify competitions organized by the clubs they
        represent, unless the competition is locked by the staff.
        """
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError(_('User not authenticated'), 403)
        if 'date_end' in data and 'date_start' in data and data['date_end'] < data['date_start']:
            raise serializers.ValidationError(_('Start date may not be later than End date.'))
        if user.is_superuser or user.is_staff:
            return data
        if (not (self.instance and self.instance.organization.group in user.groups.all()) and
                ('organization' not in data or data['organization'].group not in user.groups.all())):
            raise serializers.ValidationError(_('No permission to alter or create an competition.'), 403)
        if (self.instance and (self.instance.locked or self.instance.event.locked) or
                ('locked' in data and data['locked']) or
                (not self.instance and data['event'].locked)):
            raise serializers.ValidationError(_('No permission to alter or create a locked competition.'), 403)
        return data


class CompetitionLimitedSerializer(CompetitionSerializer):
    """
    Serializer for limited competition results
    """

    class Meta:
        model = Competition
        fields = (
            'id', 'name', 'date_start', 'date_end', 'type', 'type_info', 'level', 'level_info',
            'locked', 'public', 'trial')

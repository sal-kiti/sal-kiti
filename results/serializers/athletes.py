from abc import ABC

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.models.athletes import Athlete, AthleteInformation
from results.models.organizations import Organization
from results.serializers.organizations import OrganizationSerializer


class AthleteInformationListSerializer(serializers.ListSerializer, ABC):
    """
    ListSerializer to limit athlete additional information for nested serializer.
    """
    def to_representation(self, data):
        if not isinstance(data, list):
            user = self.context['request'].user
            if user.is_superuser:
                data = data.filter(visibility__in=['P', 'A', 'S', 'U'])
            elif user.is_staff:
                data = data.filter(visibility__in=['P', 'A', 'S'])
            elif user.is_authenticated:
                data = data.filter(visibility__in=['P', 'A'])
            else:
                data = data.filter(visibility__in=['P'])
        return super().to_representation(data)


class AthleteInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for athletes additional information.
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = AthleteInformation
        list_serializer_class = AthleteInformationListSerializer
        fields = ('id', 'athlete', 'type', 'value', 'date_start', 'date_end', 'visibility', 'permissions')


class AthleteSerializer(serializers.ModelSerializer):
    """
    Serializer for athletes.
    """
    organization_info = OrganizationSerializer(read_only=True, source='organization')
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all())
    info = AthleteInformationSerializer(many=True, read_only=True)

    permissions = DRYPermissionsField()

    class Meta:
        model = Athlete
        fields = ('id', 'first_name', 'last_name', 'sport_id', 'organization', 'organization_info',
                  'additional_organizations', 'date_of_birth', 'gender', 'info', 'permissions')

    def to_representation(self, instance):
        """
        Hide gender and date_of_birth unless POST or user is in UNMASKED_ATHLETE_USERS settings list.
        """
        data = super().to_representation(instance)
        if 'request' in self.context and self.context['request'].method != 'POST' and (
                self.context['request'].user.username not in getattr(settings, 'UNMASKED_ATHLETE_USERS', [])):
            for field in ['date_of_birth', 'gender']:
                data.pop(field, None)
        return data

    def validate(self, data):
        """
        Check permissions to create an athlete.

        External organization athletes may be created by any logged in user.
        """
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError(_('User not authenticated'), 403)
        if user.is_superuser or user.is_staff:
            return data
        if 'organization' not in data or not data['organization'].external:
            raise serializers.ValidationError(_('No permission to create non external athlete'), 403)
        return data


class AthleteLimitedSerializer(AthleteSerializer):
    """
    Serializer for athletes to users without staff permissions
    """
    organization_info = OrganizationSerializer(read_only=True, source='organization')
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all())
    info = AthleteInformationSerializer(many=True, read_only=True)

    class Meta:
        model = Athlete
        fields = ('id', 'first_name', 'last_name', 'sport_id', 'organization', 'organization_info',
                  'additional_organizations', 'info')


class AthleteNameSerializer(AthleteSerializer):
    """
    Serializer for athlete name and sport ID
    """

    class Meta:
        model = Athlete
        fields = ('id', 'first_name', 'last_name', 'sport_id')

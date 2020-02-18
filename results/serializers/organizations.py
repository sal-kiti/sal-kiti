from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.mixins.eager_loading import EagerLoadingMixin
from results.models.organizations import Area, Organization


class AreaSerializer(serializers.ModelSerializer):
    """
    Serializer for organizational area
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = Area
        fields = ('id', 'name', 'abbreviation', 'permissions')


class OrganizationSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for organizations
    """
    permissions = DRYPermissionsField()

    _PREFETCH_RELATED_FIELDS = ['areas']

    class Meta:
        model = Organization
        fields = ('id', 'name', 'abbreviation', 'external', 'areas', 'group', 'permissions')

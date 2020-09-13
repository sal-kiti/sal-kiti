from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.models.statistics import StatisticsLink


class StatisticsLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for statistics links
    """
    permissions = DRYPermissionsField()

    class Meta:
        model = StatisticsLink
        fields = ('id', 'group', 'name', 'link', 'highlight', 'order', 'public', 'permissions')

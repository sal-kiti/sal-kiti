from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.models.sports import Sport


class SportSerializer(serializers.ModelSerializer):
    """
    Serializer for sports
    """

    permissions = DRYPermissionsField()

    class Meta:
        model = Sport
        fields = ("id", "name", "abbreviation", "order", "historical", "permissions")

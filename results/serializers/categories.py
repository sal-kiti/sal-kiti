from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.models.categories import Category, Division


class DivisionSerializer(serializers.ModelSerializer):
    """
    Serializer for divisions
    """

    permissions = DRYPermissionsField()

    class Meta:
        model = Division
        fields = ("id", "name", "abbreviation", "historical", "permissions")


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories
    """

    division_info = DivisionSerializer(read_only=True, source="division")
    division = serializers.PrimaryKeyRelatedField(queryset=Division.objects.all())

    permissions = DRYPermissionsField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "abbreviation",
            "division",
            "division_info",
            "min_age",
            "max_age",
            "gender",
            "team",
            "team_size",
            "historical",
            "permissions",
        )

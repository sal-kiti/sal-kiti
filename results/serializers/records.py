from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from results.mixins.eager_loading import EagerLoadingMixin
from results.models.records import Record, RecordLevel


class RecordSerializer(serializers.ModelSerializer):
    """
    Serializer for records.
    """

    permissions = DRYPermissionsField()

    class Meta:
        model = Record
        fields = (
            "id",
            "result",
            "partial_result",
            "level",
            "type",
            "category",
            "approved",
            "date_start",
            "date_end",
            "info",
            "historical",
            "permissions",
        )

    def validate(self, data):
        """
        Validates:
        """
        user = self.context["request"].user
        if user.is_superuser or user.is_staff:
            return data
        if (
            not self.instance
            or [i for i in list(data.keys()) if i not in ["approved", "historical"]] != []
            or not (
                self.instance.level.area
                and self.instance.level.area.manager
                and self.instance.level.area.manager in user.groups.all()
                or self.instance.type.sport.is_manager(user)
            )
        ):
            raise serializers.ValidationError(_("No permission to alter or create a record."), 403)
        return data


class RecordLimitedSerializer(RecordSerializer):
    """
    Serializer for limited records.
    """

    permissions = DRYPermissionsField()

    level = serializers.SlugRelatedField(read_only=True, slug_field="abbreviation")
    category = serializers.SlugRelatedField(read_only=True, slug_field="abbreviation")

    class Meta:
        model = Record
        fields = ("id", "level", "approved", "partial_result", "category", "date_end", "historical")


class RecordLevelSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for record levels.
    """

    permissions = DRYPermissionsField()

    _PREFETCH_RELATED_FIELDS = ["levels", "types"]

    class Meta:
        model = RecordLevel
        fields = (
            "id",
            "name",
            "abbreviation",
            "levels",
            "types",
            "personal",
            "team",
            "decimals",
            "historical",
            "permissions",
        )

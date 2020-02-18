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
        fields = ('id', 'result', 'partial_result', 'level', 'type', 'category', 'approved',
                  'date_start', 'date_end', 'info', 'historical', 'permissions')


class RecordLimitedSerializer(RecordSerializer):
    """
    Serializer for limited records.
    """
    permissions = DRYPermissionsField()

    level = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )

    class Meta:
        model = Record
        fields = ('id', 'level', 'approved', 'partial_result', 'category', 'date_end', 'historical')


class RecordLevelSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for record levels.
    """
    permissions = DRYPermissionsField()

    _PREFETCH_RELATED_FIELDS = ['levels',
                                'types']

    class Meta:
        model = RecordLevel
        fields = ('id', 'name', 'abbreviation', 'levels', 'types', 'personal', 'team', 'decimals', 'historical',
                  'permissions')

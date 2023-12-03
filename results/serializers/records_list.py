from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from results.mixins.eager_loading import EagerLoadingMixin
from results.models.records import Record
from results.models.results import Result
from results.serializers.athletes import AthleteLimitedSerializer
from results.serializers.competitions import CompetitionLimitedSerializer
from results.serializers.results import ResultPartialLimitedSerializer


class ResultRecordListSerializer(serializers.ModelSerializer):
    """
    Serializer for limited result information
    """
    athlete = AthleteLimitedSerializer(read_only=True)
    competition = CompetitionLimitedSerializer(read_only=True)
    team_members = AthleteLimitedSerializer(read_only=True, many=True)

    organization = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )

    class Meta:
        model = Result
        fields = (
            'id', 'athlete', 'first_name', 'last_name',  'competition', 'organization', 'category', 'result',
            'decimals', 'team', 'team_members', 'approved')


class RecordListSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    """
    Serializer for listing records.
    """
    result = ResultRecordListSerializer(read_only=True)
    partial_result = ResultPartialLimitedSerializer(read_only=True)

    level = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )

    permissions = DRYPermissionsField()

    def get_queryset(self):
        """
        Filter to active records
        """
        queryset = Record.objects.filter(date_end=None)
        return queryset

    _PREFETCH_RELATED_FIELDS = ['result',
                                'result__athlete',
                                'result__athlete__additional_organizations',
                                'result__athlete__organization',
                                'result__athlete__organization__areas',
                                'result__competition',
                                'result__competition__level',
                                'result__competition__type',
                                'result__organization',
                                'result__organization__areas',
                                'result__team_members',
                                'partial_result',
                                'partial_result__type',
                                'level',
                                'category',
                                'type',
                                'type__sport'
                                ]

    class Meta:
        model = Record
        fields = ('id', 'result', 'partial_result', 'level', 'type', 'category', 'approved',
                  'date_start', 'date_end', 'info', 'historical', 'permissions')

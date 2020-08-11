from rest_framework import serializers

from .competitions import CompetitionSerializer
from .athletes import AthleteSerializer
from .results import ResultPartialSerializer
from ..models.results import Result


class ResultDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for a detailed information about single result
    """
    athlete = AthleteSerializer(read_only=True)
    competition = CompetitionSerializer(read_only=True)
    partial = ResultPartialSerializer(many=True, read_only=True)
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    elimination_category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )
    organization = serializers.SlugRelatedField(
        read_only=True,
        slug_field='abbreviation'
    )

    class Meta:
        model = Result
        fields = (
            'id', 'competition', 'athlete', 'organization', 'category', 'elimination_category', 'result',
            'result_code', 'position', 'approved', 'info', 'partial')

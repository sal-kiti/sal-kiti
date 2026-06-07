from django.http import JsonResponse
from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from divari.models import Competition, Result, Season, SeasonResult, Team
from divari.serializers import (
    CompetitionSerializer,
    ResultSerializer,
    SeasonResultSerializer,
    SeasonSerializer,
    TeamSerializer,
)
from divari.utils import calculate_season_results
from results.utils.pagination import CustomPagePagination


class CompetitionFilter(filters.FilterSet):
    """
    Custom filters for the event.
    """

    date_start = filters.DateFilter(field_name="date", lookup_expr="gte")
    date_end = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Competition
        fields = ["date", "organization", "date_start", "date_end"]


class CompetitionViewSet(viewsets.ModelViewSet):
    """API endpoint for divari competitions.

    list:
    Returns a list of all the existing competitions.

    retrieve:
    Returns the given competition.

    create:
    Creates a new competition instance.

    update:
    Updates a given competition.

    partial_update:
    Updates a given competition.

    destroy:
    Removes the given competition.
    """

    pagination_class = CustomPagePagination
    permission_classes = (DRYPermissions,)
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CompetitionFilter


class ResultViewSet(viewsets.ModelViewSet):
    """API endpoint for divari results.

    list:
    Returns a list of all the existing results.

    retrieve:
    Returns the given result.

    create:
    Creates a new result instance.

    update:
    Updates a given result.

    partial_update:
    Updates a given result.

    destroy:
    Removes the given result.
    """

    pagination_class = CustomPagePagination
    permission_classes = (DRYPermissions,)
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["competition", "bow_type"]


class SeasonViewSet(viewsets.ModelViewSet):
    """API endpoint for divari seasons.

    list:
    Returns a list of all the existing seasons.

    retrieve:
    Returns the given season.

    create:
    Creates a new season instance.

    update:
    Updates a given season.

    partial_update:
    Updates a given season.

    destroy:
    Removes the given season.
    """

    pagination_class = CustomPagePagination
    permission_classes = (DRYPermissions,)
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["name"]
    ordering_fields = ["date_start"]


class SeasonResultViewSet(viewsets.ModelViewSet):
    """API endpoint for divari season results.

    list:
    Returns a list of all the existing season results.

    retrieve:
    Returns the given season result.

    create:
    Creates a new season result instance.

    update:
    Updates a given season result.

    partial_update:
    Updates a given season result.

    destroy:
    Removes the given season result.
    """

    pagination_class = CustomPagePagination
    permission_classes = (DRYPermissions,)
    queryset = SeasonResult.objects.all()
    serializer_class = SeasonResultSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["team__season", "team__bow_type"]


class TeamViewSet(viewsets.ModelViewSet):
    """API endpoint for divari teams.

    list:
    Returns a list of all the existing teams.

    retrieve:
    Returns the given team.

    create:
    Creates a new team instance.

    update:
    Updates a given team.

    partial_update:
    Updates a given team.

    destroy:
    Removes the given team.
    """

    pagination_class = CustomPagePagination
    permission_classes = (DRYPermissions,)
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [filters.DjangoFilterBackend]


class CalculateSeason(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            season = request.data["season"]
            season = int(season)
            season = Season.objects.get(pk=season)
        except (KeyError, ValueError, Season.DoesNotExist):
            raise ValidationError("Invalid season")
        calculate_season_results(season)
        return JsonResponse({"season": season.pk, "calculated": "true"})

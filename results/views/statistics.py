import operator

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from drf_spectacular.utils import extend_schema
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.decorators import api_view

from results.models.competitions import CompetitionLevel
from results.models.results import Result
from results.models.statistics import StatisticsLink
from results.serializers.statistics import StatisticsLinkSerializer


class StatisticsLinkViewSet(viewsets.ModelViewSet):
    """API endpoint for statistics links.

    list:
    Returns a list of all the existing statistics links.

    retrieve:
    Returns the given statistics link.

    create:
    Creates a new statistics link instance.

    update:
    Updates a given statistics link.

    partial_update:
    Updates a given statistics link.

    destroy:
    Removes the given statistics link.
    """

    permission_classes = (DRYPermissions,)
    queryset = StatisticsLink.objects.all()
    serializer_class = StatisticsLinkSerializer

    def get_queryset(self):
        """
        Restricts the returned information to public links, unless user is
        staff or superuser.
        """
        user = self.request.user
        if not user.is_superuser and not user.is_staff:
            self.queryset = self.queryset.filter(public=True)
        return self.queryset


@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "organization": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                    "abbreviation": {"type": "string"},
                                },
                            },
                            "value": {"type": "integer"},
                        },
                    },
                }
            },
        }
    },
)
@never_cache
@api_view()
def statistics_pohjolan_malja(request, year):
    """
    Calculates organization points from SM competitions.

    First athlete or team per category gets 8 points for the organization
    they represent, second gets 7 and so on until 8th get 1 point.

    All SM competitions during a calendar year are counted.
    """
    if not request.user.is_staff:
        return JsonResponse({"message": "Forbidden"}, status=403)
    level_list = ["SM"]
    max_position = 8
    competition_levels = CompetitionLevel.objects.filter(abbreviation__in=level_list)
    results = Result.objects.filter(
        competition__level__in=competition_levels,
        position__gte=1,
        competition__date_start__year=year,
    ).order_by("competition", "category", "position", "-result")
    data_dict = {}
    competition = None
    category = None
    for result in results:
        if competition != result.competition or category != result.category:
            max_position = 8
            competition = result.competition
            category = result.category
        if result.organization.external:
            if not Result.objects.filter(
                competition=result.competition,
                category=result.category,
                position=result.position,
                organization__external=False,
            ).exists():
                max_position += 1
        elif result.position <= max_position:
            points = max_position - result.position + 1
            organization = result.organization
            if organization not in data_dict:
                data_dict[organization] = points
            else:
                data_dict[organization] = data_dict[organization] + points
    object_list = sorted(data_dict.items(), key=operator.itemgetter(1), reverse=True)
    data = []
    for obj in object_list:
        data.append({"organization": model_to_dict(obj[0], fields=["id", "name", "abbreviation"]), "value": obj[1]})
    return JsonResponse({"results": data})

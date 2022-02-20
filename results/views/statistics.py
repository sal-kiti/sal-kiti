import operator

from django.views.decorators.cache import never_cache
from django.forms.models import model_to_dict
from django.http import JsonResponse
from rest_framework.decorators import api_view

from results.models.results import Result
from results.models.competitions import CompetitionLevel


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
        return JsonResponse({'message': 'Forbidden'}, status=403)
    level_list = ['SM']
    max_position = 8
    competition_levels = CompetitionLevel.objects.filter(abbreviation__in=level_list)
    results = Result.objects.filter(competition__level__in=competition_levels, position__lte=max_position,
                                    position__gte=1, competition__date_start__year=year)
    data_dict = {}
    for result in results:
        points = max_position - result.position + 1
        organization = result.organization
        if organization not in data_dict:
            data_dict[organization] = points
        else:
            data_dict[organization] = data_dict[organization] + points
    object_list = sorted(data_dict.items(), key=operator.itemgetter(1), reverse=True)
    data = []
    for obj in object_list:
        data.append({
            'organization': model_to_dict(obj[0], fields=['id', 'name', 'abbreviation']),
            'value': obj[1]
        })
    return JsonResponse({'results': data})

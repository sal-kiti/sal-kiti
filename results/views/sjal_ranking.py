from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view

from results.models.results import Result


def _sjal_ranking_add(athlete, division, result_total, result_1440, n, n70):
    """
    Creates a result object

    :param athlete: Athlete
    :param division: division
    :param result_total: total result
    :param result_1440: 1440 round result
    :param n: number of competitions
    :param n70: number of 70m competitions
    :type athlete: Athlete object
    :type division: string
    :type result_total: int
    :type result_1440: int
    :type n: int
    :type n70: int
    :return: result object
    :rtype: dict
    """
    if n70 > 2 or division in ["yt", "nt"]:
        return {
            "athlete": {
                "id": athlete.pk,
                "first_name": athlete.first_name,
                "last_name": athlete.last_name,
                "organization": athlete.organization.abbreviation,
            },
            "result": int(result_total),
            "competitions": n,
        }
    else:
        return {
            "athlete": {
                "id": athlete.pk,
                "first_name": athlete.first_name,
                "last_name": athlete.last_name,
                "organization": athlete.organization.abbreviation,
            },
            "result": int(result_total + result_1440),
            "competitions": n,
        }


def _sjal_ranking_get_results(division):
    """
    Filters Result queryset for SJAL ranking

    :param division: division
    :type division: string
    :return: Results
    :rtype: queryset
    """
    categories_r = ["Y", "N", "17", "T17", "20", "N20", "50", "N50", "60", "N60", "70", "N70", "80", "N80"]
    categories_t = [
        "YT",
        "NT",
        "17T",
        "T17T",
        "20T",
        "N20T",
        "50T",
        "N50T",
        "60T",
        "N60T",
        "70T",
        "N70T",
        "80T",
        "N80T",
    ]
    categories_v = [
        "YV",
        "NV",
        "17V",
        "T17V",
        "20V",
        "N20V",
        "50V",
        "N50V",
        "60V",
        "N60V",
        "70V",
        "N70V",
        "80V",
        "N80V",
    ]
    categories_lb = [
        "YLB",
        "NLB",
        "17LB",
        "T17LB",
        "20LB",
        "N20LB",
        "50LB",
        "N50LB",
        "60LB",
        "N60LB",
        "70LB",
        "N70LB",
        "80LB",
        "N80LB",
    ]
    categories_tr = [
        "YTR",
        "NTR",
        "17TR",
        "T17TR",
        "20TR",
        "N20TR",
        "50TR",
        "N50TR",
        "60TR",
        "N60TR",
        "70TR",
        "N70TR",
        "80TR",
        "N80TR",
    ]
    competition_types = ["18m", "25m", "70m", "1440"]
    date_end = date.today()
    date_start = date_end - relativedelta(years=2)
    results = Result.objects.filter(
        competition__type__abbreviation__in=competition_types,
        athlete__organization__external=False,
        competition__date_end__gte=date_start,
        competition__date_start__lte=date_end,
    ).order_by("athlete", "-result")
    if division == "y":
        results = results.filter(category__abbreviation__in=categories_r).exclude(athlete__gender="W")
    elif division == "n":
        results = results.filter(category__abbreviation__in=categories_r, athlete__gender="W")
    elif division == "yt":
        results = results.filter(category__abbreviation__in=categories_t).exclude(athlete__gender="W")
    elif division == "nt":
        results = results.filter(category__abbreviation__in=categories_t, athlete__gender="W")
    elif division == "yv":
        results = results.filter(category__abbreviation__in=categories_v).exclude(athlete__gender="W")
    elif division == "nv":
        results = results.filter(category__abbreviation__in=categories_v, athlete__gender="W")
    elif division == "ylb":
        results = results.filter(category__abbreviation__in=categories_lb).exclude(athlete__gender="W")
    elif division == "nlb":
        results = results.filter(category__abbreviation__in=categories_lb, athlete__gender="W")
    elif division == "ytr":
        results = results.filter(category__abbreviation__in=categories_tr).exclude(athlete__gender="W")
    elif division == "ntr":
        results = results.filter(category__abbreviation__in=categories_tr, athlete__gender="W")
    results = results.prefetch_related("athlete", "athlete__organization", "category", "competition__type")
    return results


@cache_page(60 * 15)
@api_view()
def statistics_sjal_ranking(request, division):
    """
    Calculates SJAL ranking by archer.

    Categories that are shooting same distance and target size Y and N are included.
    Three best 18m/25m results and 2 best 70m results and the best 1440 round result (divided by 2) are included.
    Compound and barebow athletes may substitute 1440 round result with third 70m result.

    Returns JSON:
    {
        'results': [
            {
                'athlete': {
                    'id': athlete.pk,
                    'first_name': athlete.first_name,
                    'last_name': athlete.last_name,
                    'organization': athlete.organization.abbreviation
                },
                'result': result total,
                'competitions': number of competitions included (max 6)
            }
        ]
    }
    """
    if division not in ["y", "n", "yt", "nt", "yv", "nv", "ylb", "nlb", "ytr", "ntr"]:
        return JsonResponse({"results": []})
    categories_70 = {
        "y": ["Y", "N", "20", "N20"],
        "n": ["Y", "N", "20", "N20"],
        "yt": ["YT", "NT", "17T", "T17T", "20T", "N20T", "50T", "N50T", "60T", "N60T", "70T", "N70T", "80T", "N80T"],
        "nt": ["YT", "NT", "17T", "T17T", "20T", "N20T", "50T", "N50T", "60T", "N60T", "70T", "N70T", "80T", "N80T"],
        "yv": ["YV", "NV", "17V", "T17V", "20V", "N20V", "50V", "N50V", "60V", "N60V", "70V", "N70V", "80V", "N80V"],
        "nv": ["YV", "NV", "17V", "T17V", "20V", "N20V", "50V", "N50V", "60V", "N60V", "70V", "N70V", "80V", "N80V"],
        "ylb": [
            "YLB",
            "NLB",
            "17LB",
            "T17LB",
            "20LB",
            "N20LB",
            "50LB",
            "N50LB",
            "60LB",
            "N60LB",
            "70LB",
            "N70LB",
            "80LB",
            "N80LB",
        ],
        "nlb": [
            "YLB",
            "NLB",
            "17LB",
            "T17LB",
            "20LB",
            "N20LB",
            "50LB",
            "N50LB",
            "60LB",
            "N60LB",
            "70LB",
            "N70LB",
            "80LB",
            "N80LB",
        ],
        "ytr": [
            "YTR",
            "NTR",
            "17TR",
            "T17TR",
            "20TR",
            "N20TR",
            "50TR",
            "N50TR",
            "60TR",
            "N60TR",
            "70TR",
            "N70TR",
            "80TR",
            "N80TR",
        ],
        "ntr": [
            "YTR",
            "NTR",
            "17TR",
            "T17TR",
            "20TR",
            "N20TR",
            "50TR",
            "N50TR",
            "60TR",
            "N60TR",
            "70TR",
            "N70TR",
            "80TR",
            "N80TR",
        ],
    }

    categories_1440 = {
        "y": ["Y", "20"],
        "n": ["N", "N20"],
        "yt": ["YT", "20T"],
        "nt": ["NT", "17T", "N20T", "50T", "60T"],
        "yv": ["YV"],
        "nv": ["NV", "20V"],
        "ylb": ["YLB"],
        "nlb": ["NLB", "20LB"],
        "ytr": ["YTR"],
        "ntr": ["NTR", "20TR"],
    }
    competition_types_indoor = ["18m", "25m"]
    try:
        limit = int(request.GET.get("limit", 0))
    except ValueError:
        limit = 0
    if limit < 0:
        limit = 0
    ranking = []
    results = _sjal_ranking_get_results(division)
    result_total = 0
    result_1440 = 0
    n = 0
    n18 = 0
    n70 = 0
    n1440 = 0
    athlete = None
    for result in results:
        if result.result:
            if athlete and athlete != result.athlete:
                if result_total > 0 or result_1440 > 0:
                    ranking.append(_sjal_ranking_add(athlete, division, result_total, result_1440, n, n70))
                result_total = 0
                result_1440 = 0
                n = 0
                n18 = 0
                n70 = 0
                n1440 = 0
            athlete = result.athlete
            if result.competition.type.abbreviation in competition_types_indoor and n18 < 3:
                n18 += 1
                n += 1
                result_total = result_total + result.result
            elif result.competition.type.abbreviation == "1440" and n1440 < 1 and division not in ["yt", "nt"]:
                if result.category.abbreviation in categories_1440.get(division):
                    n1440 += 1
                    n += 1
                    result_1440 = result.result // 2
            elif result.competition.type.abbreviation == "70m" and n70 < 3:
                if result.category.abbreviation in categories_70.get(division):
                    n70 += 1
                    n += 1
                    if n70 == 3 and division not in ["yt", "nt"]:
                        # count only 1440 or third 70m result for total result number
                        if result_1440:
                            n -= 1
                        if result_1440 > result.result:
                            result_total = result_total + result_1440
                        else:
                            result_total = result_total + result.result
                    else:
                        result_total = result_total + result.result
            if n > 6:
                n = 6
    if result_total > 0 or result_1440 > 0:
        ranking.append(_sjal_ranking_add(athlete, division, result_total, result_1440, n, n70))
    sorted_ranking = sorted(ranking, key=lambda k: k["result"], reverse=True)
    rank = 1
    temp_rank = 1
    temp_result = 0
    for item in sorted_ranking:
        if item["result"] == temp_result:
            item["rank"] = temp_rank
        else:
            item["rank"] = rank
            temp_rank = rank
        rank += 1
        temp_result = item["result"]
    if limit:
        sorted_ranking = sorted_ranking[:limit]
    return JsonResponse({"results": sorted_ranking})


def _sjal_ranking_add_old(athlete, division, result_total, result_1440, n, n70):
    """
    Creates a result object

    :param athlete: Athlete
    :param division: division
    :param result_total: total result
    :param result_1440: 1440 round result
    :param n: number of competitions
    :param n70: number of 70m competitions
    :type athlete: Athlete object
    :type division: string
    :type result_total: int
    :type result_1440: int
    :type n: int
    :type n70: int
    :return: result object
    :rtype: dict
    """
    if n70 > 2 and (division == "compound" or division == "barebow"):
        return {
            "athlete": {
                "id": athlete.pk,
                "first_name": athlete.first_name,
                "last_name": athlete.last_name,
                "organization": athlete.organization.abbreviation,
            },
            "result": int(result_total),
            "competitions": n,
        }
    else:
        return {
            "athlete": {
                "id": athlete.pk,
                "first_name": athlete.first_name,
                "last_name": athlete.last_name,
                "organization": athlete.organization.abbreviation,
            },
            "result": int(result_total + result_1440),
            "competitions": n,
        }


def _sjal_ranking_get_results_old(division, date_start, date_end):
    """
    Filters Result queryset for SJAL ranking

    :param division: division
    :param date_start: start date
    :param date_end: end date
    :type division: string
    :type date_start: date
    :type date_end: date
    :return: Results
    :rtype: queryset
    """
    categories_recurve = ["Y", "N", "17", "T17", "20", "N20", "50", "N50", "60", "N60"]

    categories_compound = ["YT", "NT", "17T", "T17T", "20T", "N20T", "50T", "N50T", "60T", "N60T", "70T", "N70T"]
    categories_barebow = [
        "YV",
        "NV",
        "17V",
        "T17V",
        "20V",
        "N20V",
        "50V",
        "N50V",
        "60V",
        "N60V",
        "70V",
        "N70V",
        "YLB",
        "NLB",
        "17LB",
        "T17LB",
        "20LB",
        "N20LB",
        "50LB",
        "N50LB",
        "60LB",
        "N60LB",
        "70LB",
        "N70LB",
        "YI",
        "NI",
        "17I",
        "T17I",
        "20I",
        "N20I",
        "50I",
        "N50I",
        "60I",
        "N60I",
        "70I",
        "N70I",
    ]
    competition_types = ["18m", "25m", "70m", "1440"]
    if date_start and date_end and division in ["recurve", "compound", "barebow"]:
        results = Result.objects.filter(
            competition__type__abbreviation__in=competition_types,
            athlete__organization__external=False,
            competition__date_end__gte=date_start,
            competition__date_start__lte=date_end,
        ).order_by("athlete", "-result")
        if division == "recurve":
            results = results.filter(category__abbreviation__in=categories_recurve)
        elif division == "compound":
            results = results.filter(category__abbreviation__in=categories_compound)
        elif division == "barebow":
            results = results.filter(category__abbreviation__in=categories_barebow)
        results = results.prefetch_related("athlete", "athlete__organization", "category", "competition__type")
        return results
    return Result.objects.none()


@cache_page(60 * 15)
@api_view()
def statistics_sjal_ranking_old(request, division):
    """
    Calculates SJAL ranking by archer.

    Categories that are shooting same distance and target size Y and N are included.
    Three best 18m/25m results and 2 best 70m results and the best 1440 round result (divided by 2) are included.
    Compound and barebow athletes may substitute 1440 round result with third 70m result.

    Returns JSON:
    {
        'results': [
            {
                'athlete': {
                    'id': athlete.pk,
                    'first_name': athlete.first_name,
                    'last_name': athlete.last_name,
                    'organization': athlete.organization.abbreviation
                },
                'result': result total,
                'competitions': number of competitions included (max 6)
            }
        ]
    }
    """
    categories_recurve_outdoor = ["Y", "N", "20", "N20"]
    categories_barebow_1440 = ["YV", "YLB", "YI", "NV", "NLB"]
    competition_types_indoor = ["18m", "25m"]
    try:
        date_start = datetime.strptime(request.GET.get("date_start", None), "%Y-%m-%d").date()
        date_end = datetime.strptime(request.GET.get("date_end", None), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        date_start = None
        date_end = None
    try:
        limit = int(request.GET.get("limit", 0))
    except ValueError:
        limit = 0
    if limit < 0:
        limit = 0
    ranking = []
    results = _sjal_ranking_get_results_old(division, date_start, date_end)
    result_total = 0
    result_1440 = 0
    n = 0
    n18 = 0
    n70 = 0
    n1440 = 0
    athlete = None
    for result in results:
        if result.result:
            if athlete and athlete != result.athlete:
                if result_total > 0 or result_1440 > 0:
                    ranking.append(_sjal_ranking_add_old(athlete, division, result_total, result_1440, n, n70))
                result_total = 0
                result_1440 = 0
                n = 0
                n18 = 0
                n70 = 0
                n1440 = 0
            athlete = result.athlete
            if result.competition.type.abbreviation in competition_types_indoor and n18 < 3:
                n18 += 1
                n += 1
                result_total = result_total + result.result
            elif result.competition.type.abbreviation == "1440" and n1440 < 1:
                if (
                    division == "compound"
                    or (division == "recurve" and result.category.abbreviation in categories_recurve_outdoor)
                    or (division == "barebow" and result.category.abbreviation in categories_barebow_1440)
                ):
                    n1440 += 1
                    n += 1
                    result_1440 = result.result // 2
            elif result.competition.type.abbreviation == "70m":
                if (division == "compound" or division == "barebow") and n70 < 3:
                    n70 += 1
                    n += 1
                    if n70 == 3:
                        # count only 1440 or third 70m result for total result number
                        if result_1440:
                            n -= 1
                        if result_1440 > result.result:
                            result_total = result_total + result_1440
                        else:
                            result_total = result_total + result.result
                    else:
                        result_total = result_total + result.result
                elif division == "recurve" and n70 < 2 and result.category.abbreviation in categories_recurve_outdoor:
                    n70 += 1
                    n += 1
                    result_total = result_total + result.result
            if (division == "compound" or division == "barebow") and n > 6:
                n = 6
    if result_total > 0 or result_1440 > 0:
        ranking.append(_sjal_ranking_add_old(athlete, division, result_total, result_1440, n, n70))
    sorted_ranking = sorted(ranking, key=lambda k: k["result"], reverse=True)
    rank = 1
    temp_rank = 1
    temp_result = 0
    for item in sorted_ranking:
        if item["result"] == temp_result:
            item["rank"] = temp_rank
        else:
            item["rank"] = rank
            temp_rank = rank
        rank += 1
        temp_result = item["result"]
    if limit:
        sorted_ranking = sorted_ranking[:limit]
    return JsonResponse({"results": sorted_ranking})

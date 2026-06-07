from divari.models import Competition, Result, SeasonResult, Team, TeamResult


def calculate_team_results(competition, season):
    """Calculates team results for the competition.

    :param competition:
    :param season:
    :type competition: competition object
    :type season: season object
    """
    TeamResult.objects.filter(competition=competition).delete()
    bow_types = Result.objects.filter(competition=competition).values_list("bow_type", flat=True).distinct()
    for bow_type in bow_types:
        results = Result.objects.filter(competition=competition, bow_type=bow_type).order_by("-result")
        cumulative_result = 0
        count = 0
        team_number = 1
        for result in results:
            cumulative_result += result.result
            count += 1
            if count == 3 or (
                bow_type in ["junrecurve", "juncompound", "junbarebow"]
                and count == 2
                and season.date_start.year > 2022
            ):
                try:
                    team = Team.objects.get(
                        organization=competition.organization, bow_type=bow_type, number=team_number, season=season
                    )
                except Team.DoesNotExist:
                    division = getattr(season, "start_level_" + bow_type)
                    team = Team.objects.create(
                        organization=competition.organization,
                        bow_type=bow_type,
                        number=team_number,
                        season=season,
                        division=division,
                    )
                TeamResult.objects.create(competition=competition, team=team, result=cumulative_result)
                count = 0
                cumulative_result = 0
                team_number += 1


def calculate_season_results(season):
    """Calculates divari results for the season.

    :param season:
    :type season: season object
    """
    competitions = Competition.objects.filter(date__gte=season.date_start, date__lte=season.date_end)
    for competition in competitions:
        calculate_team_results(competition, season)
    SeasonResult.objects.filter(team__season=season).delete()
    teams = Team.objects.filter(season=season)
    for team in teams:
        count = 0
        cumulative_result = 0
        results = TeamResult.objects.filter(team=team).order_by("-result")
        for result in results:
            cumulative_result += result.result
            count += 1
            if count == season.result_count:
                break
        SeasonResult.objects.create(team=team, result=cumulative_result)

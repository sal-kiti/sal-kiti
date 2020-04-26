from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from results.models.categories import Category, CategoryForCompetitionType
from results.models.records import Record, RecordLevel


def _get_ages(result):
    """
    Returns possible age limits for the athlete or the team of athletes.

    :param result:
    :type result: result object
    :return max_age: youngest age in a team at the time of the competition
    :return min_age: oldest age in a team at the time of the competition
    :rtype max_age: int
    :rtype min_age: int
    """
    max_age = None
    min_age = None
    if result.team:
        athletes = result.team_members.all()
    else:
        athletes = [result.athlete]
    for athlete in athletes:
        if athlete.date_of_birth:
            age = (result.competition.date_start.year - athlete.date_of_birth.year)
            if not max_age or max_age < age:
                max_age = age
            if not min_age or min_age > age:
                min_age = age
    return max_age, min_age


def _get_gender(result):
    """
    Returns possible gender limits for the athlete or the team of athletes.

    :param result:
    :type result: result object
    :return: gender code or None
    :rtype: str
    """
    gender_list = []
    if result.team:
        for athlete in result.team_members.all():
            if athlete.gender:
                gender_list.append(athlete.gender)
    else:
        if result.athlete.gender:
            gender_list.append(result.athlete.gender)
    if 'M' in gender_list and 'W' not in gender_list:
        gender = 'M'
    elif 'M' not in gender_list and 'W' in gender_list:
        gender = 'W'
    else:
        gender = None
    return gender


def get_categories(result):
    """
    Returns the list of possible record categories for the result.

    :param result:
    :type result: result object
    :return: categories
    :rtype: QuerySet
    """
    check = CategoryForCompetitionType.objects.filter(type=result.competition.type, category=result.category).first()
    if check and not check.check_record:
        return Category.objects.none()
    if not check or not check.record_group:
        return Category.objects.filter(id=result.category.id)
    max_age, min_age = _get_ages(result)
    gender = _get_gender(result)
    categories = Category.objects.all()
    categories = categories.filter(
        Q(gender='') | Q(gender=gender),
        sport=result.competition.type.sport,
        team=result.team
        )
    if max_age is not None:
        categories = categories.filter(
            Q(max_age=None) | Q(max_age__gte=max_age)
        )
    if min_age is not None:
        categories = categories.filter(
            Q(min_age=None) | Q(min_age__lte=min_age)
        )
    if result.team:
        categories = categories.filter(
            Q(team_size=None) | Q(team_size=result.team_members.count())
        )
    categories = categories.filter(categoryforcompetitiontype__in=CategoryForCompetitionType.objects.filter(
        type=result.competition.type, record_group=check.record_group))
    return categories


def _create_record(result, record_level, category):
    """
    Creates a record for the result. Pass it it already exists.

    :param result:
    :param record_level:
    :param category:
    :type result: result object
    :type record_level: record level object
    :type category: category object
    """
    try:
        Record.objects.get_or_create(result=result, level=record_level,
                                     type=result.competition.type, category=category,
                                     date_start=result.competition.date_start)
        Record.objects.filter(approved=False,
                              result__result__lt=result.result,
                              partial_result=None,
                              level=record_level,
                              type=result.competition.type,
                              category=category,
                              date_start__gte=result.competition.date_start
                              ).delete()
    except MultipleObjectsReturned:
        pass


def _create_record_partial(partial, record_level, category):
    """
    Creates a record for the partial result. Pass it it already exists.

    :param partial:
    :param record_level:
    :param category:
    :type partial: partial result object
    :type record_level: record level object
    :type category: category object
    """
    try:
        Record.objects.get_or_create(result=partial.result, partial_result=partial, level=record_level,
                                     type=partial.result.competition.type, category=category,
                                     date_start=partial.result.competition.date_start)
        Record.objects.filter(approved=False,
                              partial_result__value__lt=partial.value,
                              level=record_level,
                              type=partial.result.competition.type,
                              category=category,
                              date_start__gte=partial.result.competition.date_start
                              ).delete()
    except MultipleObjectsReturned:
        pass


def check_records(result):
    """
    Checks possible records for the result and creates them if found.

    :param result:
    :type result: result object
    """
    Record.objects.filter(result=result, partial_result=None, approved=False).delete()
    if result.result and not result.organization.external:
        allowed_categories = get_categories(result)
        decimals = True if result.decimals else False
        if result.team:
            record_levels = RecordLevel.objects.filter(
                Q(area=None) | Q(area__in=result.organization.areas.all()),
                levels=result.competition.level,
                types=result.competition.type,
                historical=False,
                decimals=decimals,
                base=True,
                team=True)
        else:
            record_levels = RecordLevel.objects.filter(
                Q(area=None) | Q(area__in=result.organization.areas.all()),
                levels=result.competition.level,
                types=result.competition.type,
                historical=False,
                decimals=decimals,
                base=True,
                personal=True)
        for record_level in record_levels:
            for category in allowed_categories:
                if category.team:
                    if not Record.objects.filter(Q(result__result__gt=result.result) |
                                                 Q(result__result=result.result,
                                                   result__team_members__in=result.team_members.all(),
                                                   result__organization=result.organization),
                                                 date_start__lte=result.competition.date_start,
                                                 level=record_level, type=result.competition.type, date_end=None,
                                                 historical=False, category=category, partial_result=None):
                        _create_record(result, record_level, category)
                else:
                    if not Record.objects.filter(Q(result__result__gt=result.result) |
                                                 Q(result__result=result.result, result__athlete=result.athlete),
                                                 date_start__lte=result.competition.date_start,
                                                 level=record_level, type=result.competition.type, date_end=None,
                                                 historical=False, category=category, partial_result=None):
                        _create_record(result, record_level, category)


def check_records_partial(partial):
    """
    Checks possible records for the partial result and creates them if found.

    :param partial:
    :type partial: partial result object
    """
    Record.objects.filter(partial_result=partial, approved=False).delete()
    if partial.type.records and partial.value and not partial.result.organization.external:
        allowed_categories = get_categories(partial.result)
        record_levels = RecordLevel.objects.filter(
            Q(area=None) | Q(area__in=partial.result.organization.areas.all()),
            levels=partial.result.competition.level,
            types=partial.result.competition.type,
            historical=False,
            partial=True)
        for record_level in record_levels:
            for category in allowed_categories:
                if not Record.objects.filter(Q(partial_result__value__gt=partial.value) |
                                             Q(partial_result__value=partial.value,
                                               result__athlete=partial.result.athlete),
                                             date_start__lte=partial.result.competition.date_start,
                                             level=record_level, type=partial.result.competition.type, date_end=None,
                                             historical=False, category=category).exclude(partial_result=None):
                    _create_record_partial(partial, record_level, category)

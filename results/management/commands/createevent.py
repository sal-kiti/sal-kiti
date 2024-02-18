"""
Generate a event, competition and results
Only for the test and demo use

usage: ./manage.py createevent <number of athletes>
"""

import datetime
import decimal
import random

import factory
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from results.models.athletes import Athlete
from results.models.categories import Category, Sport
from results.models.competitions import (
    CompetitionLayout,
    CompetitionLevel,
    CompetitionResultType,
    CompetitionType,
)
from results.models.organizations import Organization
from results.models.records import RecordLevel
from results.models.results import Result, ResultPartial
from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.competitions import CompetitionFactory
from results.tests.factories.events import EventFactory


def _create_categories(sport=None, verbosity=1):
    """Creates listed categories if they do not exists."""
    if verbosity:
        print("Creating categories...")
    classes = [
        ["M", "M", None, None, "M"],
        ["M20", "M20", "20", None, "M"],
        ["M18", "M18", "18", None, "M"],
        ["M16", "M16", "16", None, "M"],
        ["M50", "M50", None, "50", "M"],
        ["M60", "M60", None, "60", "M"],
        ["Y70", "Y70", None, "70", None],
        ["Y75", "Y75", None, "75", None],
        ["Y80", "Y80", None, "80", None],
        ["N", "N", None, None, "W"],
        ["N20", "N20", "20", None, "W"],
        ["N18", "N18", "18", None, "W"],
        ["N16", "N16", "16", None, "W"],
        ["N50", "N50", None, "50", "W"],
        ["N60", "N60", None, "60", "W"],
        ["Y60", "Y60", None, "60", None],
        ["Y50", "Y50", None, "50", None],
        ["Y20", "Y20", None, "20", None],
        ["Y16", "Y16", None, "16", None],
        ["Y", "Y", None, None, None],
    ]

    for c in classes:
        category = Category.objects.get_or_create(
            abbreviation=c[0],
            name=c[1],
            max_age=c[2],
            min_age=c[3],
            gender=c[4],
            sport=sport,
            division=None,
            historical=False,
        )
        if verbosity > 1:
            print(category)


def _create_organizations(verbosity=1):
    """Creates listed organizations if they do not exists."""
    if verbosity:
        print("Creating organizations...")
    organizations = [
        ["Huippu", "Huippu-urheilijat"],
        ["KK", "Kyläkisaajat"],
        ["NK", "Napakymppi ry"],
        ["Arctic", "Arctic Circle"],
        ["MS", "Metsästäjät"],
    ]
    for c in organizations:
        organization = Organization.objects.get_or_create(abbreviation=c[0], name=c[1])
        if verbosity > 1:
            print(organization)


def _create_competition_types(sport=None, record_level=None, verbosity=1):
    """Creates listed competition types if they do not exists."""
    if verbosity:
        print("Creating competition types...")
    competition_types = [
        ["300KA", "300 m kivääri asentokilpailu"],
        ["300KM", "300 m kivääri makuu"],
        ["300VA", "300 m vakiokivääri asentokilpailu"],
        ["300VM", "300 m vakiokivääri makuu"],
        ["50KA", "50 m kivääri asentokilpailu"],
        ["50KM", "50 m kivääri makuu"],
        ["10I", "10 m ilmakivääri"],
        ["10IA", "10 m ilmakivääri asentokilpailu"],
        ["10IM", "10 m ilmakivääri makuu"],
    ]
    for c in competition_types:
        competition_type = CompetitionType.objects.get_or_create(
            abbreviation=c[0],
            name=c[1],
            number_of_rounds=4,
            max_result=654,
            min_result=0,
            sport=sport,
            historical=False,
            layout=1,
            team=False,
        )
        if record_level:
            record_level.types.add(competition_type[0])
        if verbosity > 1:
            print(competition_type)


def _create_competition_result_types(verbosity=1):
    """Creates layouts for competition types."""
    if verbosity:
        print("Creating competition result types and layouts...")
    for c in CompetitionType.objects.all():
        if not CompetitionResultType.objects.filter(competition_type=c).count():
            CompetitionResultType.objects.get_or_create(
                competition_type=c, name="Partial", abbreviation="part", max_result=100
            )
            CompetitionResultType.objects.get_or_create(
                competition_type=c, name="Final", abbreviation="fin", max_result=100
            )

        if not CompetitionLayout.objects.filter(type=c.layout).count():
            CompetitionLayout.objects.get_or_create(
                type=c.layout,
                label="preliminary",
                name="nolimit",
                block=0,
                row=1,
                col=0,
                order=1,
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="#", name="position", block=1, row=1, col=1, order=2
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="Athlete", name="athlete", block=1, row=1, col=2, order=3
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="Club", name="organization", block=1, row=1, col=3, order=4
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="S1", name="part-1", block=1, row=1, col=4, order=5
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="S2", name="part-2", block=1, row=1, col=5, order=6
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="Result", name="result", block=1, row=1, col=6, order=7
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="F1", name="fin-1", block=1, row=2, col=4, order=8
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="F1", name="fin-2", block=1, row=2, col=5, order=9
            )
            CompetitionLayout.objects.get_or_create(
                type=c.layout, label="Sum", name="fsum", block=1, row=2, col=6, order=10
            )


def _create_competition_levels(record_level=None, verbosity=1):
    """Creates listed competition levels if they do not exists."""
    if verbosity:
        print("Creating competition levels...")
    competition_levels = [
        ["Olympics", "Olympics", True],
        ["WC", "World Championships", True],
        ["EC", "European Championships", True],
        ["NC", "National Championships", True],
        ["Int", "International competition", True],
        ["Nat", "National competition", True],
        ["Area", "Area competition", False],
        ["Local", "Local competition", False],
    ]
    for c in competition_levels:
        competition_level = CompetitionLevel.objects.get_or_create(abbreviation=c[0], name=c[1], historical=False)
        if c[2] and record_level:
            record_level.levels.add(competition_level[0])
        if verbosity > 1:
            print(competition_level)


def create_base_data(verbosity=1):
    if verbosity:
        print("Creating base data...")
    sport = Sport.objects.get_or_create(abbreviation="Kivääri", name="Kivääri", historical=False)[0]
    record_level = RecordLevel.objects.get_or_create(name="Suomen Ennätys", abbreviation="SE")[0]
    _create_categories(sport=sport, verbosity=verbosity)
    _create_competition_types(sport=sport, record_level=record_level, verbosity=verbosity)
    _create_competition_levels(record_level=record_level, verbosity=verbosity)
    _create_competition_result_types(verbosity=verbosity)
    _create_organizations(verbosity=verbosity)


def _create_athletes(number, verbosity=1):
    """
    Creates number athletes, 50% men / 50% women
    """
    if verbosity:
        print("Creating athletes...")
    gender = "W"
    for x in range(0, number):
        if gender == "W":
            first_name = factory.Faker("first_name_female", locale=settings.FAKER_LOCALE)
        else:
            first_name = factory.Faker("first_name_male", locale=settings.FAKER_LOCALE)
        athlete = AthleteFactory.create(
            gender=gender, first_name=first_name, organization=Organization.objects.order_by("?").first()
        )
        gender = "M" if gender == "W" else "W"
        if verbosity > 1:
            print("%s: %s" % (x, athlete))


def _get_category(athlete, competition):
    """
    Gets the list of possible categories for a athlete, based on age and gender.
    """
    age = competition.date_start.year - athlete.date_of_birth.year
    categories = Category.objects.filter(
        Q(max_age=None) | Q(max_age__gte=age),
        Q(min_age=None) | Q(min_age__lte=age),
        Q(gender="") | Q(gender=athlete.gender),
        sport=competition.type.sport,
        team=False,
    )
    if categories.count() == 1:
        return categories[0]
    return categories[random.randint(0, categories.count() - 1)]


def _create_competition(event, competition_type, verbosity=1):
    """
    Creates a competition, based on event info.
    """
    if random.randint(0, 10) > 5:
        competition_date = event.date_start
    else:
        competition_date = event.date_end
    competition_level = CompetitionLevel.objects.order_by("?").first()
    competition = CompetitionFactory.create(
        event=event,
        date_start=competition_date,
        date_end=competition_date,
        name=event.name,
        organization=event.organization,
        type=competition_type,
        level=competition_level,
        location=event.location,
        layout=competition_type.layout,
    )
    if verbosity:
        print("Creating competition: %s" % competition)
    return competition


def _get_decimals(competition):
    if competition.type.sport.abbreviation == "Practical":
        decimals = 2
    elif (
        competition.type.max_result and competition.type.max_result % 10 == 0
    ) or competition.type.sport.abbreviation == "Haulikko":
        decimals = 0
    else:
        decimals = 1
    return decimals


def _create_results(competition, index, number, verbosity=1):
    """
    Creates a randomized result, including partial results for the base
    competition.
    """
    layouts = CompetitionLayout.objects.filter(type=competition.type.layout, name__icontains="-").order_by("order")
    partial_result_types = CompetitionResultType.objects.filter(competition_type=competition.type)
    index = index * number
    athletes = Athlete.objects.all()[index : index + number]
    for i in range(1, number):
        category = _get_category(athletes[i], competition)
        level = random.randint(50, 90)
        decimals = _get_decimals(competition)
        result = Result.objects.create(
            competition=competition,
            athlete=athletes[i],
            organization=athletes[i].organization,
            category=category,
            elimination_category=category,
            decimals=decimals,
            result=0,
        )
        result_sum = 0
        previous_pr_type = None
        part_sum = 0
        for layout in layouts:
            temp_decimals = decimals
            if "x" in layout.name:
                temp_decimals = 0
            if "f" not in layout.name and "sum" not in layout.name:
                pr_type = partial_result_types.filter(abbreviation=layout.name.split("-")[0])[0]
                if pr_type != previous_pr_type:
                    part_sum = 0
                previous_pr_type = pr_type
                max_result = pr_type.max_result if pr_type.max_result else 100
                if temp_decimals:
                    value = (
                        decimal.Decimal(
                            random.randint((max_result - round((max_result / level * 10))) * 10, max_result * 10)
                        )
                        / 10
                    )
                else:
                    value = decimal.Decimal(
                        random.randint((max_result - round((max_result / level * 10))), max_result)
                    )
                ResultPartial.objects.create(
                    result=result, type=pr_type, order=layout.name.split("-")[1], value=value, decimals=temp_decimals
                )
                part_sum = part_sum + value
                result_sum = result_sum + value
            elif "f" not in layout.name and "sum" in layout.name:
                pr_type = partial_result_types.filter(abbreviation=layout.name.split("-")[0])[0]
                ResultPartial.objects.create(
                    result=result,
                    type=pr_type,
                    order=layout.name.split("-")[1],
                    value=part_sum,
                    decimals=temp_decimals,
                )
                part_sum = 0
        if layouts.count() == 0:
            result_sum = decimal.Decimal(random.randint(1, 100))
        result.result = result_sum
        result.save()
        if verbosity > 1:
            print("Result %d: %s" % (i, result))


def _create_finals_partial_results(position, category_result, layouts, partial_result_types, competition_type):
    """
    Creates partial results for finals.
    """
    result_sum = 0
    fsum = None
    for p in layouts:
        if "fin" in p.name and "-" in p.name:
            pr_type = partial_result_types.filter(abbreviation=p.name.split("-")[0])[0]
            order = int(p.name.split("-")[1])
            if pr_type.max_result % 10 == 0:
                decimals = 0
            else:
                decimals = 1
            max_result = pr_type.max_result if pr_type.max_result else 50
            if (
                (competition_type in [1, 2, 20, 22] and position < 9 and order + position < 12)
                or (competition_type == 5 and position < 9 and (order < 9 or order + position < 16))
                or (competition_type in [21, 27] and position < 7 and (order < 5 or position + order < 11))
                or (competition_type == 23 and position < 9 and (order < 5 or position + order < 13))
            ):
                result = (
                    decimal.Decimal(
                        random.randint(
                            (max_result * 10) - round((max_result / 5 * position)),
                            (max_result * 10) - round((max_result / 10 * position)),
                        )
                    )
                    / 10
                )
                if not decimals:
                    result = decimal.Decimal(round(result))
                ResultPartial.objects.create(
                    result=category_result, type=pr_type, order=order, value=result, decimals=1
                )
                result_sum += result
        elif "fsum" in p.name:
            fsum = p
    if fsum:
        pr_type = partial_result_types.filter(abbreviation=p.name.split("-")[0])[0]
        max_result = pr_type.max_result if pr_type.max_result else 100
        if pr_type and max_result % 10 == 0:
            decimals = 0
        else:
            decimals = 1
        pr_type = partial_result_types.filter(abbreviation=fsum.name.split("-")[0])[0]
        order = int(fsum.name.split("-")[1])
        ResultPartial.objects.create(
            result=category_result, type=pr_type, order=order, value=result_sum, decimals=decimals
        )


def _create_finals(competition):
    """
    Creates finals and calculates position values for the results in the
    competition.
    """
    layouts = CompetitionLayout.objects.filter(type=competition.type.layout, name__icontains="-").filter(
        name__icontains="f"
    )
    partial_result_types = CompetitionResultType.objects.filter(competition_type=competition.type)
    layouts_count = layouts.count()
    categories = (
        Result.objects.filter(competition=competition)
        .order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )
    for category in categories:
        category_results = Result.objects.filter(competition=competition, category=category).order_by("-result")
        category_size = category_results.count()
        position = 1
        for category_result in category_results:
            if competition.type.sport.abbreviation == "Practical":
                if position == 1:
                    category_result.result = decimal.Decimal(100.00)
                else:
                    category_result.result = decimal.Decimal(
                        round(100 / (random.randint(position + 10, position * 2 + 10) / 10), 2)
                    )
            category_result.position = position
            category_result.position_pre = position
            category_result.save()
            if layouts_count > 0 and category_size > 3 and position < 9:
                _create_finals_partial_results(
                    position, category_result, layouts, partial_result_types, competition.type.id
                )
            position += 1


class Command(BaseCommand):
    """Creates an event with competitions and results.

    number: Number of athletes in the event.
    -b: Create base data needed for results.

    Creates athletes, categories and competition types if they do not exist.
    """

    args = "None"
    help = "Create event"

    def add_arguments(self, parser):
        parser.add_argument("number", type=int, help="Number of athletes in the event")
        parser.add_argument("-b", action="store_true", dest="base_data", help="Create base data")

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        number = options["number"]
        if number < 1:
            print("Number of athletes must be a positive integer")
            exit(1)
        if options["base_data"]:
            create_base_data(verbosity=verbosity)
        number_of_athletes = number * CompetitionType.objects.all().count()
        current_athletes = Athlete.objects.all().count() - number_of_athletes
        if current_athletes < 0:
            _create_athletes(-current_athletes, verbosity=verbosity)
        for sport in Sport.objects.all():
            event = EventFactory.create(
                organization=Organization.objects.order_by("?").first(),
                date_start=datetime.date.today() - datetime.timedelta(days=random.randint(1, 500)),
            )
            if random.randint(0, 10) > 2:
                event.date_end = event.date_start + datetime.timedelta(days=1)
            else:
                event.date_end = event.date_start
            event.save()
            index = 0
            for competition_type in CompetitionType.objects.filter(sport=sport, team=False):
                competition = _create_competition(event, competition_type, verbosity=verbosity)
                _create_results(competition, index, number, verbosity=verbosity)
                _create_finals(competition)
                index += 1

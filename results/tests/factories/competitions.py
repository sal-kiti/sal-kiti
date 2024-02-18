import datetime
from decimal import Decimal

import factory
from django.conf import settings

from results.models.competitions import (
    Competition,
    CompetitionLayout,
    CompetitionLevel,
    CompetitionResultType,
    CompetitionType,
)
from results.tests.factories.categories import SportFactory
from results.tests.factories.events import EventFactory
from results.tests.factories.organizations import OrganizationFactory


class CompetitionLevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompetitionLevel
        django_get_or_create = ("abbreviation",)

    name = factory.Faker("company")
    abbreviation = factory.Faker("company_suffix")


class CompetitionTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompetitionType
        django_get_or_create = ("abbreviation",)

    name = factory.Faker("currency_name")
    abbreviation = factory.Faker("currency_code")
    sport = factory.SubFactory(SportFactory)
    layout = 1
    number_of_rounds = 2
    max_result = Decimal("1000.000")
    min_result = Decimal("0.000")
    personal = True


class CompetitionLayoutFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompetitionLayout
        django_get_or_create = ("order", "row")

    type = 1
    label = "S1"
    name = "elim"
    block = 1
    row = 1
    col = 1
    order = 1
    hide = "md"
    show = ""


class CompetitionResultTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompetitionResultType
        django_get_or_create = ("abbreviation",)

    competition_type = factory.SubFactory(CompetitionTypeFactory)
    name = "Elimination"
    abbreviation = "elim"
    max_result = Decimal("500.000")
    min_result = Decimal("0.000")


class CompetitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Competition

    name = factory.Faker("street_name", locale=settings.FAKER_LOCALE)
    date_start = datetime.date.today()
    date_end = datetime.date.today() + datetime.timedelta(days=1)
    location = factory.Faker("city", locale=settings.FAKER_LOCALE)
    organization = factory.SubFactory(OrganizationFactory)
    type = factory.SubFactory(CompetitionTypeFactory)
    level = factory.SubFactory(CompetitionLevelFactory)
    event = factory.SubFactory(EventFactory)
    layout = 1
    locked = True
    public = True

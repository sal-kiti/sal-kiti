import factory
from factory import fuzzy

from results.models.results import Result, ResultPartial
from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.categories import CategoryFactory
from results.tests.factories.competitions import (
    CompetitionFactory,
    CompetitionResultTypeFactory,
)
from results.tests.factories.organizations import OrganizationFactory


class ResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Result
        django_get_or_create = ("athlete", "competition")

    competition = factory.SubFactory(CompetitionFactory)
    athlete = factory.SubFactory(AthleteFactory)
    organization = factory.SubFactory(OrganizationFactory)
    category = factory.SubFactory(CategoryFactory)
    elimination_category = category
    result = fuzzy.FuzzyDecimal(0.000, 1000.000, 3)
    decimals = 1
    position = fuzzy.FuzzyInteger(1, 100)
    approved = True
    public = True


class ResultPartialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ResultPartial
        django_get_or_create = ("result", "type", "order")

    result = factory.SubFactory(ResultFactory)
    type = factory.SubFactory(CompetitionResultTypeFactory)
    order = 1
    value = fuzzy.FuzzyDecimal(0.000, 100.000, 3)
    time = None

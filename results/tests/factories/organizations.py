import factory
from factory import fuzzy

from results.models.organizations import Area, Organization


class AreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Area
        django_get_or_create = ("abbreviation",)

    name = factory.Faker("city")
    abbreviation = fuzzy.FuzzyChoice(["Club", "ABC", "Athlete", "Kings", "Queens"])


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization
        django_get_or_create = ("name",)

    name = factory.Faker("city")
    abbreviation = fuzzy.FuzzyChoice(["Club", "ABC", "Athlete", "Kings", "Queens"])

import datetime
from random import randint

import factory
from factory import fuzzy
from django.conf import settings

from results.models.athletes import Athlete, AthleteInformation
from results.tests.factories.organizations import OrganizationFactory


class AthleteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Athlete
        django_get_or_create = ('sport_id',)

    if randint(1, 2) == 1:
        gender = 'W'
    else:
        gender = 'M'
    if gender == 'W':
        first_name = factory.Faker('first_name_female', locale=settings.FAKER_LOCALE)
    else:
        first_name = factory.Faker('first_name_male', locale=settings.FAKER_LOCALE)
    last_name = factory.Faker('last_name', locale=settings.FAKER_LOCALE)
    sport_id = factory.Faker('ean8')
    date_of_birth = fuzzy.FuzzyDate(datetime.date(1950, 1, 1), datetime.date(2010, 1, 1))
    organization = factory.SubFactory(OrganizationFactory)


class AthleteInformationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AthleteInformation
    athlete = factory.SubFactory(AthleteFactory)
    type = 'Medal'
    value = 'Olympic Gold 2000'
    visibility = 'P'

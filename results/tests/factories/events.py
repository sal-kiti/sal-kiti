import datetime

import factory
from django.conf import settings

from results.models.events import Event
from results.tests.factories.organizations import OrganizationFactory


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event
        django_get_or_create = ("name",)

    name = factory.Faker("street_name", locale=settings.FAKER_LOCALE)
    date_start = datetime.date.today()
    date_end = datetime.date.today() + datetime.timedelta(days=1)
    location = factory.Faker("city", locale=settings.FAKER_LOCALE)
    organization = factory.SubFactory(OrganizationFactory)
    locked = True
    public = True

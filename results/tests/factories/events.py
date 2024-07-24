import datetime

import factory
from django.conf import settings

from results.models.events import Event, EventContact
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


class EventContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventContact
        django_get_or_create = ("event", "type")

    event = factory.SubFactory(EventFactory)
    type = "contact"
    athlete = None
    first_name = factory.Faker("first_name", locale=settings.FAKER_LOCALE)
    last_name = factory.Faker("last_name", locale=settings.FAKER_LOCALE)
    email = factory.Faker("email", locale=settings.FAKER_LOCALE)
    phone = ""

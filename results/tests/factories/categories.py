import factory

from results.models.categories import Category, Division
from results.models.sports import Sport


class SportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sport
        django_get_or_create = ("abbreviation",)

    name = "Code Sport"
    abbreviation = "Sport"


class DivisionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Division
        django_get_or_create = ("abbreviation",)

    name = "Code Division"
    abbreviation = "Code"


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("abbreviation",)

    name = "Code Juniors"
    abbreviation = "CJ"
    division = factory.SubFactory(DivisionFactory)
    max_age = 20
    min_age = 17
    gender = "M"
    historical = False

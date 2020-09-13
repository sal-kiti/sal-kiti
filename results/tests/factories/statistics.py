import factory

from results.models.statistics import StatisticsLink


class StatisticsLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StatisticsLink
        django_get_or_create = ('name',)

    name = 'Junior 11'
    group = 'Junior Qualification'
    link = '?category=11&link=true'

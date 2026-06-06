from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.competitions import CompetitionFactory
from results.tests.factories.events import EventFactory
from results.tests.factories.results import ResultFactory, ResultPartialFactory
from results.views.competitions import CompetitionViewSet
from results.views.events import EventViewSet
from results.views.results import ResultList, ResultPartialViewSet, ResultViewSet


class DatabaseQueryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.factory = APIRequestFactory()
        self.events = [EventFactory.create(name=str(n)) for n in range(2)]
        self.competitions = [CompetitionFactory.create(name=str(n), event=self.events[0]) for n in range(2)]
        self.athletes = [AthleteFactory.create(sport_id=str(n)) for n in range(2)]
        self.results = [
            ResultFactory.create(athlete=self.athletes[n], competition=self.competitions[0]) for n in range(2)
        ]
        self.partial_results = [ResultPartialFactory.create(value=n, result=self.results[0]) for n in range(2)]

    def test_number_of_queries(self):
        request = self.factory.get("/api/events/1/")
        view = EventViewSet.as_view(actions={"get": "list"})
        with self.assertNumQueries(8):
            view(request)
        request = self.factory.get("/api/competitions/1/")
        view = CompetitionViewSet.as_view(actions={"get": "list"})
        with self.assertNumQueries(9):
            view(request)
        request = self.factory.get("/api/results/1/")
        view = ResultViewSet.as_view(actions={"get": "list"})
        with self.assertNumQueries(4):
            view(request)
        request = self.factory.get("/api/partialresults/1/")
        view = ResultPartialViewSet.as_view(actions={"get": "list"})
        with self.assertNumQueries(2):
            view(request)
        request = self.factory.get("/api/resultlist/1/")
        view = ResultList.as_view(actions={"get": "list"})
        with self.assertNumQueries(20):
            view(request)
        [ResultFactory.create(competition=self.competitions[0]) for _ in range(2)]
        with self.assertNumQueries(20):
            view(request)

import json

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status

from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.categories import CategoryFactory
from results.tests.factories.competitions import (
    CompetitionFactory,
    CompetitionTypeFactory,
)
from results.tests.factories.results import ResultFactory


class SJALRankingTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        user = User.objects.create(username="tester")
        self.client.force_login(user)
        self.ct_70m = CompetitionTypeFactory(abbreviation="70m")

    def test_sjal_ranking_calculations(self):
        ct_18m = CompetitionTypeFactory(abbreviation="18m")
        ct_1440 = CompetitionTypeFactory(abbreviation="1440")
        athlete = AthleteFactory.create(gender="W")
        category = CategoryFactory.create(abbreviation="N")
        for result in [500, 500, 500, 400]:
            competition = CompetitionFactory.create(name=str(result), type=ct_18m)
            ResultFactory.create(athlete=athlete, category=category, competition=competition, result=result)
        for result in [600, 600, 500, 500]:
            competition = CompetitionFactory.create(name=str(result), type=self.ct_70m)
            ResultFactory.create(athlete=athlete, category=category, competition=competition, result=result)
        url = reverse("sjal-ranking-v2", kwargs={"division": "n"})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data["results"]), 1)
        self.assertEqual(3200, response_data["results"][0]["result"])
        for result in [1300, 1200]:
            competition = CompetitionFactory.create(name=str(result), type=ct_1440)
            ResultFactory.create(athlete=athlete, category=category, competition=competition, result=result)
        ResultFactory.create(
            athlete=AthleteFactory.create(gender="W"), category=category, competition=competition, result=1401
        )
        cache.clear()
        response = self.client.get(url, follow=True)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data["results"]), 2)
        self.assertEqual(3350, response_data["results"][0]["result"])
        self.assertEqual(700, response_data["results"][1]["result"])
        old_url = (
            reverse("sjal-ranking", kwargs={"division": "recurve"}) + "?date_start=2000-01-01&date_end=2100-01-01"
        )
        response = self.client.get(old_url, follow=True)
        response_data = json.loads(response.content)
        self.assertEqual(3350, response_data["results"][0]["result"])

    def test_sjal_ranking_invalid_division_returns_empty_list(self):
        url = reverse("sjal-ranking-v2", kwargs={"division": "invalid"})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["results"], [])

    def test_sjal_ranking_missing_date_returns_empty_list(self):
        ResultFactory.create(
            athlete=AthleteFactory.create(gender="YT"),
            category=CategoryFactory.create(abbreviation="Y"),
            result=1400,
            competition=CompetitionFactory.create(type=self.ct_70m),
        )

        old_url = reverse("sjal-ranking", kwargs={"division": "compound"})
        response = self.client.get(old_url, follow=True)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["results"], [])

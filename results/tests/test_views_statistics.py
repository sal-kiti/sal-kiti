import json
import logging

from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import RequestFactory, TestCase
from rest_framework import status

from results.models.competitions import CompetitionLevel
from results.tests.factories.competitions import CompetitionFactory
from results.tests.factories.organizations import OrganizationFactory
from results.tests.factories.results import ResultFactory


class StatisticsPohjolanMaljaTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('sal-pohjolan-malja', kwargs={'year': date.today().year})
        self.logger = logging.getLogger('django.request')
        self.previous_level = self.logger.getEffectiveLevel()
        self.logger.setLevel(logging.ERROR)

    def tearDown(self):
        self.logger.setLevel(self.previous_level)

    def test_pohjolanmalja_access_object_without_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pohjolanmalja_access_object_with_normal_user(self):
        user = User.objects.create(username='tester', first_name="Testname")
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pohjolanmalja_access_object_with_staff(self):
        level = CompetitionLevel.objects.create(name='SM', abbreviation='SM')
        org1 = OrganizationFactory.create(abbreviation="A", name="AN")
        org2 = OrganizationFactory.create(abbreviation="B", name="BN")
        competition = CompetitionFactory.create(level=level)
        ResultFactory.create(organization=org1, competition=competition, position=1)
        ResultFactory.create(organization=org1, competition=competition, position=5)
        ResultFactory.create(organization=org1, competition=competition, position=15)
        ResultFactory.create(organization=org2, competition=competition, position=9)
        ResultFactory.create(organization=org2, competition=competition, position=5)
        user = User.objects.create(username="superuser", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = [
            {
                "organization": {
                    "id": 1,
                    "name": "AN",
                    "abbreviation": "A"
                },
                "value": 12
            },
            {
                "organization": {
                    "id": 2,
                    "name": "BN",
                    "abbreviation": "B"
                },
                "value": 4
            }
        ]
        self.assertEqual(response.content.decode(), json.dumps({"results": data}))

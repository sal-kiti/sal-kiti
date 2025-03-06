import json
import logging
from datetime import date

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

from results.models.competitions import CompetitionLevel
from results.models.statistics import StatisticsLink
from results.tests.factories.competitions import CompetitionFactory
from results.tests.factories.organizations import OrganizationFactory
from results.tests.factories.results import ResultFactory
from results.tests.factories.statistics import StatisticsLinkFactory
from results.tests.utils import ResultsTestCase
from results.views.statistics import StatisticsLinkViewSet


class StatisticsLinkTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username="tester")
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = StatisticsLinkFactory.create()
        self.data = {
            "name": self.object.name,
            "group": self.object.group,
            "link": self.object.link,
            "public": self.object.public,
            "highlight": self.object.highlight,
            "order": self.object.order,
        }
        self.newdata = {"name": "New Statistics Link", "group": "Old Group", "link": "?new=link"}
        self.url = "/api/statisticslinks/"
        self.viewset = StatisticsLinkViewSet
        self.model = StatisticsLink

    def test_statistics_link_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={"get": "list"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistics_link_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_statistics_link_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_statistics_link_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_statistics_link_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistics_link_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistics_link_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_statistics_link_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_statistics_link_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_statistics_link_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_statistics_link_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_statistics_link_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_statistics_link_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_statistics_link_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_statistics_link_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_statistics_link_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class StatisticsPohjolanMaljaTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse("sal-pohjolan-malja", kwargs={"year": date.today().year})
        self.logger = logging.getLogger("django.request")
        self.previous_level = self.logger.getEffectiveLevel()
        self.logger.setLevel(logging.ERROR)

    def tearDown(self):
        self.logger.setLevel(self.previous_level)

    def test_pohjolanmalja_access_object_without_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pohjolanmalja_access_object_with_normal_user(self):
        user = User.objects.create(username="tester", first_name="Testname")
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pohjolanmalja_access_object_with_staff(self):
        level = CompetitionLevel.objects.create(name="SM", abbreviation="SM")
        org1 = OrganizationFactory.create(abbreviation="A", name="AN")
        org2 = OrganizationFactory.create(abbreviation="B", name="BN")
        competition = CompetitionFactory.create(level=level)
        ResultFactory.create(organization=org1, competition=competition, position=1)
        ResultFactory.create(organization=org1, competition=competition, position=2)
        ResultFactory.create(organization=org2, competition=competition, position=2)
        result3 = ResultFactory.create(organization=org2, competition=competition, position=3)
        ResultFactory.create(organization=org2, competition=competition, position=4)
        ResultFactory.create(organization=org1, competition=competition, position=5)
        ResultFactory.create(organization=org1, competition=competition, position=6)
        ResultFactory.create(organization=org1, competition=competition, position=7)
        ResultFactory.create(organization=org1, competition=competition, position=8)
        ResultFactory.create(organization=org2, competition=competition, position=9)
        ResultFactory.create(organization=org1, competition=competition, position=10)
        user = User.objects.create(username="superuser", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = [
            {"organization": {"id": 1, "name": "AN", "abbreviation": "A"}, "value": 25},
            {"organization": {"id": 2, "name": "BN", "abbreviation": "B"}, "value": 18},
        ]
        self.assertEqual(json.dumps({"results": data}), response.content.decode())
        org3 = OrganizationFactory.create(abbreviation="C", name="CN", external=True)
        ResultFactory.create(organization=org3, competition=competition, position=1)
        response = self.client.get(self.url, follow=True)
        # No change as org3 is tied to non-external organization
        self.assertEqual(json.dumps({"results": data}), response.content.decode())
        result3.organization = org3
        result3.save()
        response = self.client.get(self.url, follow=True)
        data = [
            {"organization": {"id": 1, "name": "AN", "abbreviation": "A"}, "value": 29},
            {"organization": {"id": 2, "name": "BN", "abbreviation": "B"}, "value": 14},
        ]
        # Org2 loses third place and places 4-9 are increased by 1 (+4 to org1, -5+1 to org2)
        self.assertEqual(json.dumps({"results": data}), response.content.decode())

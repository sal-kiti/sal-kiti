import json

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status

from results.models.organizations import Area, Organization


class UserInfoTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse("current-user")

    def test_userinfo_access_object_without_user(self):
        data = {
            "is_authenticated": False,
            "is_superuser": False,
            "is_staff": False,
            "first_name": "",
            "last_name": "",
            "email": "",
            "manager": [],
        }
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), json.dumps(data))

    def _test_userinfo_access(self, user):
        data = {
            "is_authenticated": True,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "manager": [],
        }
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), json.dumps(data))

    def test_userinfo_access_object_with_normal_user(self):
        user = User.objects.create(username="tester", first_name="Testname")
        self._test_userinfo_access(user)

    def test_userinfo_access_object_with_superuser(self):
        user = User.objects.create(username="superuser", is_superuser=True, email="admin@example.org")
        self._test_userinfo_access(user)

    def test_area_info(self):
        area = Area.objects.create(name="Area", abbreviation="area")
        org = Organization.objects.create(name="Org", abbreviation="org")
        org.areas.add(area)
        org2 = Organization.objects.create(name="Org2", abbreviation="org2")
        org2.areas.add(area)
        user = User.objects.create(username="tester", first_name="Testname")
        user.groups.add(area.group)
        data = {
            "is_authenticated": True,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "manager": [org.pk, org2.pk],
        }
        self.client.force_login(user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), json.dumps(data))

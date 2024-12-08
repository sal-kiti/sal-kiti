from django.contrib.auth.models import Group, User
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory

from results.models.events import Event, EventContact
from results.models.organizations import Area
from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.competitions import CompetitionFactory
from results.tests.factories.events import EventContactFactory, EventFactory
from results.tests.utils import ResultsTestCase
from results.views.events import EventContactViewSet, EventViewSet


class EventTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username="tester")
        self.group = Group.objects.create(name="testgroup")
        self.organization_user = User.objects.create(username="tester_2")
        self.organization_user.groups.add(self.group)
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = EventFactory.create()
        self.object.organization.group = self.group
        self.object.organization.save()
        self.data = {
            "name": self.object.name,
            "date_start": self.object.date_start.strftime("%Y-%m-%d"),
            "date_end": self.object.date_end.strftime("%Y-%m-%d"),
            "location": self.object.location,
            "organization": self.object.organization.pk,
        }
        self.newdata = {
            "name": "New Year",
            "date_start": self.object.date_start.strftime("%Y-%m-%d"),
            "date_end": self.object.date_end.strftime("%Y-%m-%d"),
            "location": "City Field",
            "organization": self.object.organization.pk,
            "toc_agreement": True,
        }
        self.updatedata = {"name": "Change Event"}
        self.url = "/api/events/"
        self.viewset = EventViewSet
        self.model = Event

    def test_event_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={"get": "list"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_event_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_event_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_update_with_organizational_user(self):
        self.object.locked = False
        self.object.save()
        response = self._test_update(user=self.organization_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_update_with_organizational_user_locked(self):
        response = self._test_update(user=self.organization_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_update_with_area_user_locked(self):
        area = Area.objects.create(name="Area 1", abbreviation="area1")
        self.user.groups.add(area.group)
        self.object.organization.areas.add(area)
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_publish_with_staffruser(self):
        self.object.public = False
        self.object.save()
        response = self._test_patch(user=self.staff_user, data={"public": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(EVENT_PUBLISH_REQUIRES_STAFF=False)
    def test_event_publish_with_organizational_user_permitted(self):
        self.object.locked = False
        self.object.public = False
        self.object.save()
        response = self._test_patch(user=self.organization_user, data={"public": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(EVENT_PUBLISH_REQUIRES_STAFF=True)
    def test_event_publish_with_organizational_user_not_permitted(self):
        self.object.locked = False
        self.object.public = False
        self.object.save()
        response = self._test_patch(user=self.organization_user, data={"public": True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_event_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_event_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_create_with_organization_user(self):
        response = self._test_create(user=self.organization_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_delete_with_organization_user(self):
        self.object.locked = False
        self.object.save()
        response = self._test_delete(user=self.organization_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_event_delete_approved_with_organization_user(self):
        self.object.locked = True
        self.object.save()
        response = self._test_delete(user=self.organization_user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(APPROVE_COMPETITIONS_WITH_EVENT=False)
    def test_event_approval_do_not_approve_competitions(self):
        competition = CompetitionFactory.create(event=self.object)
        self._test_patch(user=self.staff_user, data={"approved": True})
        competition.refresh_from_db()
        self.assertFalse(competition.approved)

    @override_settings(APPROVE_COMPETITIONS_WITH_EVENT=True)
    def test_event_approval_approve_competitions(self):
        competition = CompetitionFactory.create(event=self.object)
        self._test_patch(user=self.staff_user, data={"approved": True})
        competition.refresh_from_db()
        self.assertTrue(competition.approved)

    @override_settings(REMOVE_COMPETITION_APPROVAL_WITH_EVENT=False)
    def test_event_remove_approval_do_not_remove_competition_approval(self):
        self.object.approved = True
        self.object.save()
        competition = CompetitionFactory.create(event=self.object, approved=True)
        self._test_patch(user=self.staff_user, data={"approved": False})
        competition.refresh_from_db()
        self.assertTrue(competition.approved)

    @override_settings(REMOVE_COMPETITION_APPROVAL_WITH_EVENT=True)
    def test_event_remove_approval_remove_competition_approval(self):
        self.object.approved = True
        self.object.save()
        competition = CompetitionFactory.create(event=self.object, approved=True)
        self._test_patch(user=self.staff_user, data={"approved": False})
        competition.refresh_from_db()
        self.assertFalse(competition.approved)

    def test_event_include_competitions(self):
        competition = CompetitionFactory.create(event=self.object)
        self._test_patch(user=self.staff_user, data={"approved": True, "include_competitions": True})
        competition.refresh_from_db()
        self.assertTrue(competition.approved)

    def test_event_include_competitions_remove(self):
        self.object.approved = True
        self.object.save()
        competition = CompetitionFactory.create(event=self.object, approved=True)
        self._test_patch(user=self.staff_user, data={"approved": False, "include_competitions": True})
        competition.refresh_from_db()
        self.assertFalse(competition.approved)

    def test_event_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_event_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class EventContactTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username="tester")
        self.group = Group.objects.create(name="testgroup")
        self.organization_user = User.objects.create(username="tester_2")
        self.organization_user.groups.add(self.group)
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.athlete = AthleteFactory.create()
        self.object = EventContactFactory.create(athlete=self.athlete)
        self.object.event.organization.group = self.group
        self.object.event.organization.save()
        self.data = {
            "event": self.object.event.pk,
            "first_name": self.object.first_name,
            "last_name": self.object.last_name,
            "type": self.object.type,
            "email": self.object.email,
            "phone": self.object.phone,
        }
        self.newdata = {
            "event": self.object.event.pk,
            "first_name": self.athlete.first_name,
            "last_name": self.athlete.last_name,
            "type": "manager",
            "email": "manager@example.org",
            "phone": "+1234567890",
            "athlete": self.athlete.id,
        }
        self.url = "/api/eventcontacts/"
        self.viewset = EventContactViewSet
        self.model = EventContact

    def test_eventcontact_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={"get": "list"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_eventcontact_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eventcontact_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eventcontact_access_object_with_organization_user(self):
        response = self._test_access(user=self.organization_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_eventcontact_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_eventcontact_create_with_organization_user(self):
        response = self._test_create(user=self.organization_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_eventcontact_delete_with_organization_user(self):
        self.object.event.locked = False
        self.object.event.save()
        response = self._test_delete(user=self.organization_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_eventcontact_delete_with_organization_user_locked_event(self):
        response = self._test_delete(user=self.organization_user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

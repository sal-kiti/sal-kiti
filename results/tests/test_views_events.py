from django.contrib.auth.models import Group, User
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APIRequestFactory

from results.models.events import Event
from results.tests.factories.events import EventFactory
from results.tests.utils import ResultsTestCase
from results.views.events import EventViewSet


class EventTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.group = Group.objects.create(name="testgroup")
        self.organization_user = User.objects.create(username='tester_2')
        self.organization_user.groups.add(self.group)
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = EventFactory.create()
        self.object.organization.group = self.group
        self.object.organization.save()
        self.data = {'name': self.object.name, 'date_start': self.object.date_start.strftime('%Y-%m-%d'),
                     'date_end': self.object.date_end.strftime('%Y-%m-%d'), 'location': self.object.location,
                     'organization': self.object.organization.pk}
        self.newdata = {'name': 'New Year', 'date_start': self.object.date_start.strftime('%Y-%m-%d'),
                        'date_end': self.object.date_end.strftime('%Y-%m-%d'), 'location': 'City Field',
                        'organization': self.object.organization.pk, 'toc_agreement': True}
        self.updatedata = {'name': 'Change Event'}
        self.url = '/api/events/'
        self.viewset = EventViewSet
        self.model = Event

    def test_event_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
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

    def test_event_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_event_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

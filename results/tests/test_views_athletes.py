from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from results.models.athletes import Athlete, AthleteInformation
from results.tests.factories.athletes import AthleteFactory, AthleteInformationFactory
from results.views.athletes import AthleteViewSet, AthleteInformationViewSet


class AthleteTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = AthleteFactory.create()
        self.data = {'id': 1, 'first_name': self.object.first_name, 'last_name': self.object.last_name,
                     'sport_id': self.object.sport_id, 'organization': self.object.organization.pk,
                     'date_of_birth': self.object.date_of_birth.strftime("%Y-%m-%d"), 'gender': self.object.gender}
        self.limited_data = {'id': 1, 'first_name': self.object.first_name, 'last_name': self.object.last_name,
                             'sport_id': self.object.sport_id, 'organization': self.object.organization.pk}
        self.update_data = {'id': 1, 'first_name': 'John', 'last_name': 'Doe', 'sport_id': '1234567890',
                            'organization': self.object.organization.pk, 'date_of_birth': '1983-02-03',
                            'gender': 'M'}
        self.newdata = {'first_name': 'John', 'last_name': 'Doe', 'sport_id': '222222222',
                        'organization': self.object.organization.pk, 'date_of_birth': '1983-02-03',
                        'gender': 'M'}
        self.url = '/api/athletes/'
        self.viewset = AthleteViewSet
        self.model = Athlete

    def _test_access(self, user):
        request = self.factory.get(self.url + '1/')
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        return view(request, pk=self.object.pk)

    def _test_create(self, user, data):
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'post': 'create'})
        return view(request)

    def _test_delete(self, user):
        request = self.factory.delete(self.url + '1/')
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        return view(request, pk=1)

    def _test_update(self, user, data):
        request = self.factory.put(self.url + '1/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'put': 'update'})
        return view(request, pk=1)

    def test_athlete_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_athlete_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.limited_data:
            self.assertEqual(response.data[key], self.data[key])

    def test_athlete_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.limited_data:
            self.assertEqual(response.data[key], self.data[key])

    def test_athlete_update_without_user(self):
        response = self._test_update(user=None, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_athlete_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.update_data:
            if key in ['date_of_birth', 'gender']:
                self.assertEqual(response.data[key], "*")
            else:
                self.assertEqual(response.data[key], self.update_data[key])

    def test_athlete_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.update_data:
            if key in ['date_of_birth', 'gender']:
                self.assertEqual(response.data[key], "*")
            else:
                self.assertEqual(response.data[key], self.update_data[key])

    def test_athlete_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_athlete_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_athlete_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_athlete_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_athlete_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_athlete_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_athlete_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_athlete_create_external_with_normal_user(self):
        self.object.organization.external = True
        self.object.organization.save()
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_athlete_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_athlete_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_athlete_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AthleteInformationTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.athlete = AthleteFactory.create()
        self.object = AthleteInformationFactory.create(athlete=self.athlete)
        self.object_private = AthleteInformationFactory.create(athlete=self.athlete, visibility='S')
        self.data = {'id': 1, 'athlete': self.object.athlete.pk, 'type': self.object.type,
                     'value': self.object.value, 'visibility': self.object.visibility}
        self.update_data = {'id': 1, 'athlete': self.object.athlete.pk, 'type': self.object.type,
                            'value': "Field Champion 2018", 'visibility': self.object.visibility}
        self.newdata = {'athlete': self.object.athlete.pk, 'type': self.object.type,
                        'value': "Field Champion 2000", 'visibility': 'A'}
        self.url = '/api/athleteinformation/'
        self.viewset = AthleteInformationViewSet
        self.model = AthleteInformation

    def _test_access(self, user):
        request = self.factory.get(self.url + '1/')
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        return view(request, pk=self.object.pk)

    def _test_create(self, user, data):
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'post': 'create'})
        return view(request)

    def _test_delete(self, user):
        request = self.factory.delete(self.url + '1/')
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        return view(request, pk=1)

    def _test_update(self, user, data):
        request = self.factory.put(self.url + '1/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'put': 'update'})
        return view(request, pk=1)

    def test_athlete_information_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_athlete_information_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_athlete_information_access_object_A(self):
        self.object.visibility = 'A'
        self.object.save()
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_athlete_information_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_athlete_information_access_object_S(self):
        self.object.visibility = 'S'
        self.object.save()
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_athlete_information_access_object_U(self):
        self.object.visibility = 'U'
        self.object.save()
        response = self._test_access(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_athlete_information_update_without_user(self):
        response = self._test_update(user=None, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_athlete_information_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_athlete_information_update_with_staff_user(self):
        response = self._test_update(user=self.staff_user, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_athlete_information_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_athlete_information_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_athlete_information_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 3)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_athlete_information_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_athlete_information_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 3)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_athlete_information_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_athlete_information_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_athlete_information_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_athlete_information_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_athlete_information_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

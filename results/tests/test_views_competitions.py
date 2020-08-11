from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from results.models.competitions import CompetitionLevel, CompetitionType, CompetitionResultType, Competition
from results.models.competitions import CompetitionLayout
from results.tests.factories.competitions import CompetitionFactory, CompetitionLevelFactory, CompetitionTypeFactory
from results.tests.factories.competitions import CompetitionResultTypeFactory, CompetitionLayoutFactory
from results.tests.utils import ResultsTestCase
from results.views.competitions import CompetitionLevelViewSet, CompetitionTypeViewSet, CompetitionResultTypeViewSet
from results.views.competitions import CompetitionViewSet, CompetitionLayoutViewSet


class CompetitionLevelTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = CompetitionLevelFactory.create()
        self.data = {'name': self.object.name, 'abbreviation': self.object.abbreviation,
                     'historical': self.object.historical}
        self.newdata = {'name': 'Championships', 'abbreviation': 'Champ'}
        self.url = '/api/competitionlevels/'
        self.viewset = CompetitionLevelViewSet
        self.model = CompetitionLevel

    def test_competition_level_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_level_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_competition_level_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_competition_level_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_level_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_level_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_level_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_level_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_level_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_level_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_competition_level_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_level_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_competition_level_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_level_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_level_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_competition_level_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CompetitionTypeTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = CompetitionTypeFactory.create()
        self.data = {'name': self.object.name, 'abbreviation': self.object.abbreviation,
                     'number_of_rounds': self.object.number_of_rounds, 'max_result': self.object.max_result,
                     'min_result': self.object.min_result, 'historical': self.object.historical}
        self.newdata = {'name': '50 yards', 'abbreviation': '50y', 'number_of_rounds': 2}
        self.url = '/api/competitiontypes/'
        self.viewset = CompetitionTypeViewSet
        self.model = CompetitionType

    def test_competition_type_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_type_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key in ['max_result', 'min_result']:
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_competition_type_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key in ['max_result', 'min_result']:
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_competition_type_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_type_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_type_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_type_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_type_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_type_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_type_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_competition_type_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_type_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_competition_type_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_type_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_type_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_competition_type_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CompetitionResultTypeTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = CompetitionResultTypeFactory.create()
        self.data = {'competition_type': self.object.competition_type.id, 'name': self.object.name,
                     'abbreviation': self.object.abbreviation, 'max_result': self.object.max_result,
                     'min_result': self.object.min_result}
        self.newdata = {'competition_type': self.object.competition_type.id, 'name': 'Finals', 'abbreviation': "fin"}
        self.url = '/api/competitionresulttypes/'
        self.viewset = CompetitionResultTypeViewSet
        self.model = CompetitionResultType

    def test_competition_result_type_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_result_type_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key in ['max_result', 'min_result']:
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_competition_result_type_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key in ['max_result', 'min_result']:
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_competition_result_type_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_result_type_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_result_type_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_result_type_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_result_type_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_result_type_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_result_type_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_competition_result_type_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_result_type_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_competition_result_type_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_result_type_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_result_type_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_competition_result_type_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CompetitionLayoutTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = CompetitionLayoutFactory.create()
        self.data = {'type': self.object.type, 'name': self.object.name,
                     'label': self.object.label, 'block': self.object.block, 'row': self.object.row,
                     'col': self.object.col, 'order': self.object.order, 'hide': self.object.hide,
                     'show': self.object.show}
        self.newdata = {'type': self.object.type, 'name': self.object.name,
                        'label': self.object.label, 'block': 2, 'row': 2, 'col': 2, 'order': 2,
                        'hide': self.object.hide, 'show': self.object.show}
        self.url = '/api/competitiontypelayouts/'
        self.viewset = CompetitionLayoutViewSet
        self.model = CompetitionLayout

    def test_competition_type_layout_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_type_layout_access_object_without_user(self):
        request = self.factory.get(self.url + '1/')
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        response = view(request, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_competition_type_layout_update_without_user(self):
        request = self.factory.post(self.url + '1/', self.newdata)
        view = self.viewset.as_view(actions={'put': 'update'})
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_type_layout_create_without_user(self):
        request = self.factory.post(self.url, self.newdata)
        view = self.viewset.as_view(actions={'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_type_layout_access_object_with_normal_user(self):
        request = self.factory.get(self.url + '1/')
        force_authenticate(request, user=self.user)
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        response = view(request, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_competition_type_layout_update_with_normal_user(self):
        request = self.factory.post(self.url + '1/', self.newdata)
        force_authenticate(request, user=self.user)
        view = self.viewset.as_view(actions={'put': 'update'})
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_type_layout_create_with_normal_user(self):
        request = self.factory.post(self.url, self.newdata)
        force_authenticate(request, user=self.user)
        view = self.viewset.as_view(actions={'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_type_layout_update_with_superuser(self):
        request = self.factory.put(self.url + '1/', self.newdata)
        force_authenticate(request, user=self.superuser)
        view = self.viewset.as_view(actions={'put': 'update'})
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_type_layout_create_with_superuser(self):
        request = self.factory.post(self.url, self.newdata)
        force_authenticate(request, user=self.superuser)
        view = self.viewset.as_view(actions={'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)

    def test_competition_type_layout_create_existing_with_superuser(self):
        request = self.factory.post(self.url, self.data)
        force_authenticate(request, user=self.superuser)
        view = self.viewset.as_view(actions={'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.model.objects.all().count(), 1)

    def test_competition_type_layout_delete_with_user(self):
        request = self.factory.delete(self.url + '1/')
        force_authenticate(request, user=self.user)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_type_layout_delete_with_superuser(self):
        request = self.factory.delete(self.url + '1/')
        force_authenticate(request, user=self.superuser)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CompetitionTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.group = Group.objects.create(name="testgroup")
        self.organization_user = User.objects.create(username='tester_2')
        self.organization_user.groups.add(self.group)
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = CompetitionFactory.create()
        self.object.organization.group = self.group
        self.object.organization.save()
        self.object.event.organization.group = self.group
        self.object.event.organization.group.save()
        self.data = {'name': self.object.name, 'date_start': self.object.date_start.strftime('%Y-%m-%d'),
                     'date_end': self.object.date_end.strftime('%Y-%m-%d'), 'location': self.object.location,
                     'type': self.object.type.pk, 'level': self.object.level.pk,
                     'organization': self.object.organization.pk, 'event': self.object.event.pk,
                     'locked': self.object.locked, 'public': self.object.public}
        self.newdata = {'name': 'Village Yearly', 'date_start': self.object.date_start.strftime('%Y-%m-%d'),
                        'date_end': self.object.date_end.strftime('%Y-%m-%d'), 'location': 'Village Field',
                        'type': self.object.type.pk, 'level': self.object.level.pk,
                        'organization': self.object.organization.pk, 'event': self.object.event.pk}
        self.updatedata = {'name': 'Change Competition'}
        self.url = '/api/competitions/'
        self.viewset = CompetitionViewSet
        self.model = Competition

    def _test_access(self, user):
        request = self.factory.get(self.url + '1/')
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        return view(request, pk=self.object.pk)

    def _test_create(self, user, data, locked=True):
        if not locked:
            self.object.event.locked = False
            self.object.event.save()
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'post': 'create'})
        return view(request)

    def _test_delete(self, user, locked=True):
        if not locked:
            self.object.event.locked = False
            self.object.event.save()
        request = self.factory.delete(self.url + '1/')
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        return view(request, pk=1)

    def _test_update(self, user, data, locked=True):
        if not locked:
            self.object.event.locked = False
            self.object.event.save()
        request = self.factory.put(self.url + '1/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'put': 'update'})
        return view(request, pk=1)

    def _test_patch(self, user, data, locked=True):
        if not locked:
            self.object.event.locked = False
            self.object.event.save()
        request = self.factory.patch(self.url + '1/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'patch': 'partial_update'})
        return view(request, pk=1)

    def test_competition_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_competition_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_competition_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_update_with_organizational_user(self):
        self.object.locked = False
        self.object.save()
        response = self._test_update(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_competition_update_with_organizational_user_locked(self):
        response = self._test_update(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_update_with_organizational_user_event_locked(self):
        self.object.locked = False
        self.object.save()
        response = self._test_update(user=self.organization_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_publish_with_staffruser(self):
        self.object.public = False
        self.object.save()
        response = self._test_patch(user=self.staff_user, data={"public": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(COMPETITION_PUBLISH_REQUIRES_STAFF=False)
    def test_competition_publish_with_organizational_user_permitted(self):
        self.object.locked = False
        self.object.public = False
        self.object.save()
        response = self._test_patch(user=self.organization_user, data={"public": True}, locked=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(COMPETITION_PUBLISH_REQUIRES_STAFF=True)
    def test_competition_publish_with_organizational_user_not_permitted(self):
        self.object.locked = False
        self.object.public = False
        self.object.save()
        response = self._test_patch(user=self.organization_user, data={"public": True}, locked=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_competition_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_competition_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_competition_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_competition_create_with_organization_user(self):
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_competition_create_with_organization_user_not_locked_competition(self):
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_competition_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_competition_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_competition_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_competition_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

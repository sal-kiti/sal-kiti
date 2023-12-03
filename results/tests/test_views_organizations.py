from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APIRequestFactory

from results.models.organizations import Area, Organization
from results.tests.factories.organizations import AreaFactory, OrganizationFactory
from results.tests.utils import ResultsTestCase
from results.views.organizations import AreaViewSet, OrganizationViewSet


class OrganizationTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.staff_user = User.objects.create(username='staffuser', is_staff=True)
        self.superuser = User.objects.create(username='superuser', is_superuser=True)
        self.object = OrganizationFactory.create()
        self.data = {'name': self.object.name, 'abbreviation': self.object.abbreviation}
        self.newdata = {'name': 'Club Zero', 'abbreviation': 'Zero'}
        self.url = '/api/organizations/'
        self.viewset = OrganizationViewSet
        self.model = Organization

    def test_organization_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_organization_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_organization_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organization_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organization_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_organization_group_is_created(self):
        self.assertEqual(Group.objects.all().count(), 1)
        self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(Group.objects.all().count(), 2)
        self.assertEqual(Group.objects.get(id=2).name, 'club_Zero_2')
        self.assertEqual(Group.objects.get(id=2).organization.name, 'Club Zero')

    def test_organization_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_organization_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_organization_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_organization_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_organization_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class OrganizationManagerTestCase(ResultsTestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.area1 = Area.objects.create(name="Area 1", abbreviation="area1")
        self.area2 = Area.objects.create(name="Area 2", abbreviation="area2")
        self.organization1 = Organization.objects.create(name="Organization 1", abbreviation="org1")
        self.organization2 = Organization.objects.create(name="Organization 2", abbreviation="org2")
        self.organization3 = Organization.objects.create(name="Organization 3", abbreviation="org3")
        self.organization1.areas.add(self.area1)
        self.organization2.areas.add(self.area1)
        self.organization2.areas.add(self.area2)

    def test_organization_manager_get_user_organizations(self):
        self.user.groups.add(Group.objects.get(name="area_area1"))
        self.assertEqual(Organization.objects.get_user_organizations(self.user).count(), 2)
        self.user.groups.add(Group.objects.get(name="area_area2"))
        self.assertEqual(Organization.objects.get_user_organizations(self.user).count(), 3)
        self.user.groups.add(Group.objects.get(name="club_org3_" + str(self.organization3.pk)))
        self.assertEqual(Organization.objects.get_user_organizations(self.user).count(), 4)

    def test_organization_check_if_user_is_manager(self):
        self.user.groups.add(Group.objects.get(name="area_area2"))
        self.user.groups.add(Group.objects.get(name="club_org3_" + str(self.organization3.pk)))
        self.assertFalse(self.organization1.is_manager(self.user))
        self.assertTrue(self.organization2.is_manager(self.user))
        self.assertTrue(self.organization3.is_manager(self.user))
        self.assertTrue(self.organization2.is_area_manager(self.user))
        self.assertFalse(self.organization3.is_area_manager(self.user))


class AreaTestCase(ResultsTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = AreaFactory.create()
        self.data = {'name': self.object.name, 'abbreviation': self.object.abbreviation}
        self.newdata = {'name': 'Area Zero', 'abbreviation': 'AZ'}
        self.url = '/api/area/'
        self.viewset = AreaViewSet
        self.model = Area

    def test_area_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_area_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_area_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_area_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_area_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_area_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_area_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_area_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_area_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_area_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_area_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_area_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_area_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_area_group_is_created(self):
        self.assertEqual(Group.objects.all().count(), 1)
        self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(Group.objects.all().count(), 2)
        self.assertEqual(Group.objects.get(id=2).name, 'area_AZ')
        self.assertEqual(Group.objects.get(id=2).area.name, 'Area Zero')

    def test_area_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_area_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_area_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

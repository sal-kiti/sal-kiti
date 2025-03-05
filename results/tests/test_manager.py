from django.contrib.auth.models import Group, User

from results.models.organizations import Area, Organization
from results.models.sports import Sport
from results.tests.utils import ResultsTestCase


class OrganizationManagerTestCase(ResultsTestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
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


class SportManagerTestCase(ResultsTestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.sport = Sport.objects.create(name="Sport", abbreviation="sport")

    def test_sport_manager_get_user_sports(self):
        self.assertFalse(self.sport.is_manager(self.user))
        self.user.groups.add(Group.objects.get(name="sport_sport"))
        self.assertTrue(self.sport.is_manager(self.user))

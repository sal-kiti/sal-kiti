from decimal import Decimal
from datetime import date, time

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from results.models.athletes import AthleteInformation
from results.models.categories import CategoryForCompetitionType
from results.models.results import Result, ResultPartial
from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.competitions import CompetitionResultTypeFactory
from results.tests.factories.results import ResultFactory, ResultPartialFactory
from results.views.results import ResultViewSet, ResultPartialViewSet, ResultList


class ResultTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.group = Group.objects.create(name="testgroup")
        self.organization_user = User.objects.create(username='tester_2')
        self.organization_user.groups.add(self.group)
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.object = ResultFactory.create(athlete=AthleteFactory.create(
            gender="M", date_of_birth=date.today() - relativedelta(years=18)))
        self.object.competition.organization.group = self.group
        self.object.competition.organization.save()
        self.athlete = AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=18))
        self.data = {'competition': self.object.competition.id, 'athlete': self.object.athlete.id,
                     'first_name': self.object.athlete.first_name, 'last_name': self.object.athlete.last_name,
                     'organization': self.object.organization.id, 'category': self.object.category.id,
                     'elimination_category': self.object.elimination_category.id, 'result': self.object.result,
                     'result_code': self.object.result_code, 'decimals': self.object.decimals,
                     'position': self.object.position, 'approved': self.object.approved}
        self.newdata = {'competition': self.object.competition.id, 'athlete': self.athlete.id,
                        'first_name': 'John', 'last_name': 'Doe',
                        'organization': self.object.organization.id, 'category': self.object.category.id,
                        'elimination_category': self.object.elimination_category.id, 'result': None,
                        'result_code': 'DNF', 'decimals': 0,
                        'position': None, 'approved': False}
        self.competition_result_type = CompetitionResultTypeFactory.create(
                competition_type=self.object.competition.type)
        self.url = '/api/results/'
        self.viewset = ResultViewSet
        self.model = Result

    def test_result_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _test_access(self, user):
        request = self.factory.get(self.url + '1/')
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        return view(request, pk=self.object.pk)

    def _test_create(self, user, data, locked=True):
        if not locked:
            self.object.competition.locked = False
            self.object.competition.save()
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'post': 'create'})
        return view(request)

    def _test_delete(self, user, locked=True):
        if not locked:
            self.object.competition.locked = False
            self.object.competition.save()
        request = self.factory.delete(self.url + '1/')
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        return view(request, pk=1)

    def _test_update(self, user, data, locked=True):
        if not locked:
            self.object.competition.locked = False
            self.object.competition.save()
        request = self.factory.put(self.url + '1/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'put': 'update'})
        return view(request, pk=1)

    def _create_category_limit(self):
        CategoryForCompetitionType.objects.create(category=self.object.category, type=self.object.competition.type,
                                                  max_result=self.object.competition.type.max_result - 1,
                                                  min_result=self.object.competition.type.min_result + 1)

    def test_result_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key == 'result':
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_result_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key == 'result':
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_result_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_result_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_result_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_result_update_with_organizational_user(self):
        self.object.approved = False
        self.object.save()
        response = self._test_update(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_result_update_with_organizational_user_locked(self):
        response = self._test_update(user=self.organization_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_result_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_result_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_result_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_result_create_with_superuser_dry_run(self):
        data = self.newdata
        data.update({'dry_run': True})
        response = self._test_create(user=self.superuser, data=data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 1)

    def test_result_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_result_create_with_staff_user_locked_competition(self):
        response = self._test_create(user=self.staff_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_with_staff_user_not_locked_competition(self):
        response = self._test_create(user=self.staff_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_with_organization_user(self):
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_with_organization_user_not_locked_competition(self):
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_with_organization_user_requiring_approval(self):
        self.object.competition.level.require_approval = True
        self.object.competition.level.save()
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_with_organization_user_requiring_approval_and_approved(self):
        self.object.competition.level.require_approval = True
        self.object.competition.level.save()
        self.object.competition.approved = True
        self.object.competition.save()
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_with_normal_user_not_locked_competition(self):
        response = self._test_create(user=self.user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_too_high(self):
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.max_result + 1)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_max_result(self):
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.max_result)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_too_low(self):
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.min_result - 1)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_min_result(self):
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.min_result)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_too_high_with_category_limit(self):
        self._create_category_limit()
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.max_result)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_max_result_with_category_limit(self):
        self._create_category_limit()
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.max_result - 1)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_too_low_with_category_limit(self):
        self._create_category_limit()
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.min_result)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_min_result_with_category_limit(self):
        self._create_category_limit()
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.min_result + 1)
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_incorrect_gender(self):
        athlete_gender = AthleteFactory.create(gender="W", date_of_birth=date.today() - relativedelta(years=18))
        self.data['athlete'] = athlete_gender.pk
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.data['non_field_errors'][0], "Athlete's gender is not allowed for this category.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_too_young(self):
        athlete_young = AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=16))
        self.data['athlete'] = athlete_young.pk
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.data['non_field_errors'][0], "Athlete is too young for this category.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_too_young_exact_limit(self):
        self.object.category.age_exact = True
        self.object.category.save()
        athlete_young = AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=17)
                                              + relativedelta(days=1))
        self.data['athlete'] = athlete_young.pk
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.data['non_field_errors'][0], "Athlete is too young for this category.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_old_enough_exact_limit(self):
        self.object.category.age_exact = True
        self.object.category.save()
        athlete_young = AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=17))
        self.data['athlete'] = athlete_young.pk
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_too_old(self):
        athlete_old = AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=21))
        self.data['athlete'] = athlete_old.pk
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.data['non_field_errors'][0], "Athlete is too old for this category.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_too_old_exact_limit(self):
        self.object.category.age_exact = True
        self.object.category.save()
        athlete_old = AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=20))
        self.data['athlete'] = athlete_old.pk
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.data['non_field_errors'][0], "Athlete is too old for this category.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_create_young_enough_exact_limit(self):
        self.object.category.age_exact = True
        self.object.category.save()
        athlete_old = AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=20)
                                            + relativedelta(days=1))
        self.data['athlete'] = athlete_old.pk
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_category_now_allowed(self):
        CategoryForCompetitionType.objects.create(category=self.object.category, type=self.object.competition.type,
                                                  disallow=True)
        self.data['athlete'] = self.athlete.pk
        self.data['result'] = Decimal(self.object.competition.type.max_result)
        response = self._test_create(user=self.staff_user, data=self.data, locked=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['non_field_errors'][0], 'Category is not allowed for this competition type.')

    def test_result_create_without_type_requirement(self):
        self.data['athlete'] = self.athlete.pk
        self.object.competition.type.requirements = 'licence'
        self.object.competition.type.save()
        response = self._test_create(user=self.staff_user, data=self.data, locked=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['non_field_errors'][0], 'Missing requirement: licence.')

    def test_result_create_with_type_requirement(self):
        self.data['athlete'] = self.athlete.pk
        self.object.competition.type.requirements = 'licence'
        self.object.competition.type.save()
        AthleteInformation.objects.create(athlete=self.athlete,
                                          type='licence',
                                          value='ok',
                                          date_start=self.object.competition.date_start,
                                          date_end=self.object.competition.date_end)
        response = self._test_create(user=self.staff_user, data=self.data, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_create_without_level_requirement(self):
        self.data['athlete'] = self.athlete.pk
        self.object.competition.level.requirements = 'licence'
        self.object.competition.level.save()
        response = self._test_create(user=self.staff_user, data=self.data, locked=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['non_field_errors'][0], 'Missing requirement: licence.')

    def test_result_create_with_level_requirement(self):
        self.data['athlete'] = self.athlete.pk
        self.object.competition.level.requirements = 'licence'
        self.object.competition.level.save()
        AthleteInformation.objects.create(athlete=self.athlete,
                                          type='licence',
                                          value='ok',
                                          date_start=self.object.competition.date_start,
                                          date_end=self.object.competition.date_end)
        response = self._test_create(user=self.staff_user, data=self.data, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_result_delete_with_user(self):
        response = self._test_delete(user=self.user, locked=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_result_delete_with_organization_user(self):
        self.object.approved = False
        self.object.save()
        response = self._test_delete(user=self.organization_user, locked=False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_result_delete_with_organization_user_locked(self):
        self.object.approved = False
        self.object.save()
        response = self._test_delete(user=self.organization_user, locked=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_result_delete_approved_with_organization_user(self):
        self.object.approved = True
        self.object.save()
        response = self._test_delete(user=self.organization_user, locked=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_result_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser, locked=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_result_recursive_delete_with_superuser(self):
        competition_result_type = CompetitionResultTypeFactory.create(
                competition_type=self.object.competition.type)
        partial = ResultPartialFactory.create(result=self.object,
                                              type=competition_result_type).pk
        response = self._test_delete(user=self.superuser, locked=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ResultPartial.objects.filter(pk=partial).count(), 0)

    def test_result_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user, locked=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_result_update_with_partial_result(self):
        self.newdata['partial'] = [
            {"order": 1, "type": self.competition_result_type.pk, "value": Decimal('10.000'), "decimals": 0}
        ]
        response = self._test_update(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['partial']), 1)

    def test_result_update_with_partial_change_result(self):
        self.test_result_update_with_partial_result()
        self.newdata['partial'] = [
            {"order": 1, "type": self.competition_result_type.pk, "value": Decimal('15.000'), "decimals": 0}
        ]
        response = self._test_update(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(len(response.data['partial']), 1)
        self.assertEqual(response.data['partial'][0]['value'], '15.000')

    def test_result_update_with_partial_change_result_too_high(self):
        self.test_result_update_with_partial_result()
        self.newdata['partial'] = [{"order": 1, "type": self.competition_result_type.pk, "value": 550, "decimals": 0}]
        response = self._test_update(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.data['non_field_errors'][0], "A result is too high.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_result_update_with_partial_delete_result(self):
        self.test_result_update_with_partial_result()
        self.newdata['partial'] = []
        response = self._test_update(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(len(response.data['partial']), 0)

    def test_result_create_with_team_result(self):
        team_members = [self.athlete.pk,
                        AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=19)).pk,
                        AthleteFactory.create(gender="M", date_of_birth=date.today() - relativedelta(years=20)).pk]
        self.newdata['athlete'] = None
        self.newdata['team_members'] = team_members
        self.newdata['team'] = True
        response = self._test_create(user=self.superuser, data=self.newdata, locked=False)
        self.assertEqual(len(response.data['team_members']), 3)


class PartialResultTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.group = Group.objects.create(name="testgroup")
        self.organization_user = User.objects.create(username='tester_2')
        self.organization_user.groups.add(self.group)
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.result = ResultFactory.create()
        self.competition_result_type = CompetitionResultTypeFactory.create(
                competition_type=self.result.competition.type)
        self.incorrect_competition_result_type = CompetitionResultTypeFactory.create(abbreviation="part")
        self.object = ResultPartialFactory.create(result=self.result,
                                                  type=self.competition_result_type)
        self.result.competition.organization.group = self.group
        self.result.competition.organization.save()
        self.data = {'result': self.object.result.id, 'type': self.object.type.id, 'order': self.object.order,
                     'value': self.object.value}
        self.newdata = {'result': self.object.result.id, 'type': self.object.type.id, 'order': 2,
                        'value': Decimal('10.000')}
        self.url = '/api/resultpartials/'
        self.viewset = ResultPartialViewSet
        self.model = ResultPartial

    def test_partial_result_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _test_access(self, user):
        request = self.factory.get(self.url + '1/')
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        return view(request, pk=self.object.pk)

    def _test_create(self, user, data, locked=True):
        if not locked:
            self.object.result.competition.locked = False
            self.object.result.competition.save()
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'post': 'create'})
        return view(request)

    def _test_delete(self, user, locked=True):
        if not locked:
            self.object.result.competition.locked = False
            self.object.result.competition.save()
        request = self.factory.delete(self.url + '1/')
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        return view(request, pk=1)

    def _test_update(self, user, data, locked=True):
        if not locked:
            self.object.result.competition.locked = False
            self.object.result.competition.save()
        request = self.factory.put(self.url + '1/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'put': 'update'})
        return view(request, pk=1)

    def test_partial_result_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key in ['value']:
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_partial_result_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            if key in ['value']:
                self.assertEqual(response.data[key], str(self.data[key]))
            else:
                self.assertEqual(response.data[key], self.data[key])

    def test_partial_result_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_result_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_result_update_with_staffuser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_result_update_with_organizational_user(self):
        self.object.result.approved = False
        self.object.result.save()
        response = self._test_update(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_result_update_with_organizational_user_locked(self):
        response = self._test_update(user=self.organization_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_result_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_result_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_result_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            if key in ['value']:
                self.assertEqual(response.data[key], str(self.newdata[key]))
            else:
                self.assertEqual(response.data[key], self.newdata[key])

    def test_partial_result_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 2)
        for key in self.newdata:
            if key in ['value']:
                self.assertEqual(response.data[key], str(self.newdata[key]))
            else:
                self.assertEqual(response.data[key], self.newdata[key])

    def test_partial_result_create_with_staff_user_locked_competition(self):
        response = self._test_create(user=self.staff_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_partial_result_create_with_staff_user_not_locked_competition(self):
        response = self._test_create(user=self.staff_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_partial_result_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_with_organization_user(self):
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_with_organization_user_not_locked_competition(self):
        self.object.result.approved = False
        self.object.result.save()
        response = self._test_create(user=self.organization_user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_partialresult_text_value(self):
        data = {'result': self.object.result.id, 'type': self.object.type.id, 'order': 2,
                'text': 'Text result value'}
        response = self._test_create(user=self.staff_user, data=data, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], 'Text result value')
        self.assertEqual(response.data['value'], None)

    def test_partialresult_time_value(self):
        data = {'result': self.object.result.id, 'type': self.object.type.id, 'order': 2,
                'time': time(hour=14, minute=20, second=29).isoformat()}
        response = self._test_create(user=self.staff_user, data=data, locked=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['time'], '14:20:29')

    def test_partial_result_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_with_normal_user_not_locked_competition(self):
        response = self._test_create(user=self.user, data=self.newdata, locked=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_delete_with_user(self):
        response = self._test_delete(user=self.user, locked=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_result_delete_with_organization_user(self):
        self.object.result.approved = False
        self.object.result.save()
        response = self._test_delete(user=self.organization_user, locked=False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_partial_result_delete_with_organization_user_locked(self):
        self.object.result.approved = False
        self.object.result.save()
        response = self._test_delete(user=self.organization_user, locked=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_result_delete_approved_with_organization_user(self):
        self.object.result.approved = False
        self.object.result.save()
        response = self._test_delete(user=self.organization_user, locked=False)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_partial_result_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser, locked=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_partial_result_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user, locked=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_partial_result_create_with_incorrect_type(self):
        self.newdata['type'] = self.incorrect_competition_result_type.pk
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_too_high(self):
        self.newdata['value'] = Decimal(self.competition_result_type.max_result + 1)
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_max_result(self):
        self.newdata['value'] = Decimal(self.competition_result_type.max_result)
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_partial_result_create_too_high_team(self):
        self.object.result.category.team = True
        self.object.result.category.team_size = 3
        self.object.result.category.save()
        self.newdata['value'] = Decimal(self.competition_result_type.max_result * 3 + 1)
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_max_result_team(self):
        self.object.result.category.team = True
        self.object.result.category.team_size = 3
        self.object.result.category.save()
        self.newdata['value'] = Decimal(self.competition_result_type.max_result * 3)
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_partial_result_create_too_low(self):
        self.newdata['value'] = Decimal(self.competition_result_type.min_result - 1)
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_result_create_min_result(self):
        self.newdata['value'] = Decimal(self.competition_result_type.min_result)
        response = self._test_create(user=self.superuser, data=self.newdata, locked=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ResultListTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.factory = APIRequestFactory()
        self.result = ResultFactory.create(athlete=AthleteFactory.create(
            gender="M", date_of_birth=date.today() - relativedelta(years=18)))
        self.result2 = ResultFactory.create(athlete=self.result.athlete)
        self.url = '/api/resultlist/'
        self.viewset = ResultList
        self.model = Result

    def test_result_list_access(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_result_list_search(self):
        import os
        if 'TRAVIS' not in os.environ:
            params = {'sport': 1, 'group_results': 2}
            request = self.factory.get(self.url, params)
            view = self.viewset.as_view(actions={'get': 'list'})
            response = view(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['result'], str(self.result.result + self.result2.result))

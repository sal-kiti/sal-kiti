from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from results.models.categories import Category, CategoryForCompetitionType
from results.models.organizations import Area
from results.models.records import Record, RecordLevel
from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.competitions import (
    CompetitionFactory,
    CompetitionResultTypeFactory,
)
from results.tests.factories.results import ResultFactory, ResultPartialFactory
from results.views.records import RecordViewSet


class RecordsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username="tester")
        self.staff_user = User.objects.create(username="staffuser", is_staff=True)
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.competition = CompetitionFactory.create()
        self.competition_later = CompetitionFactory(
            date_start=self.competition.date_start + timedelta(days=2),
            date_end=self.competition.date_end + timedelta(days=2),
            type=self.competition.type,
            level=self.competition.level,
        )
        sport = self.competition.type.sport
        self.category_W = Category.objects.create(
            name="W", abbreviation="W", max_age=None, min_age=None, gender="W", sport=sport
        )
        self.category_M = Category.objects.create(
            name="M", abbreviation="M", max_age=None, min_age=None, gender="M", sport=sport
        )
        self.category_W20_2 = Category.objects.create(
            name="W2", abbreviation="W2", max_age=20, min_age=None, gender="W", sport=sport
        )
        self.category_W20 = Category.objects.create(
            name="W", abbreviation="W", max_age=20, min_age=None, gender="W", sport=sport
        )
        self.category_W50 = Category.objects.create(
            name="W", abbreviation="W", max_age=None, min_age=50, gender="W", sport=sport
        )
        self.category_team = Category.objects.create(
            name="Team", abbreviation="Team", max_age=None, min_age=None, gender=None, team=True, sport=sport
        )
        self.category_check = CategoryForCompetitionType.objects.create(
            type=self.competition.type, category=self.category_W, record_group=1
        )
        CategoryForCompetitionType.objects.create(type=self.competition.type, category=self.category_M, record_group=1)
        self.category_check_W20 = CategoryForCompetitionType.objects.create(
            type=self.competition.type, category=self.category_W20, record_group=1
        )
        CategoryForCompetitionType.objects.create(
            type=self.competition.type, category=self.category_W50, record_group=1
        )
        CategoryForCompetitionType.objects.create(
            type=self.competition.type, category=self.category_W20_2, record_group=2
        )
        self.athlete = AthleteFactory.create(gender="W", date_of_birth=date.today() - timedelta(days=18 * 365))
        self.athlete2 = AthleteFactory.create(
            gender="W", date_of_birth=date.today() - timedelta(days=18 * 365), sport_id=self.athlete.sport_id + "2"
        )
        self.athlete_old = AthleteFactory.create(gender="W", date_of_birth=date.today() - timedelta(days=70 * 365))
        self.record_level = RecordLevel.objects.create(
            name="SE", abbreviation="SE", base=True, decimals=True, team=True
        )
        self.record_level_partial = RecordLevel.objects.create(
            name="Finals SE", abbreviation="FSE", base=False, decimals=True, partial=True
        )
        self.record_level.types.add(self.competition.type)
        self.record_level_partial.types.add(self.competition.type)
        self.record_level.levels.add(self.competition.level)
        self.record_level_partial.levels.add(self.competition.level)
        self.area_group = Group.objects.create(name="AreaGroup")
        self.area = Area.objects.create(name="Area", abbreviation="A", manager=self.area_group)
        self.record_level_area = RecordLevel.objects.create(
            name="Area", abbreviation="A", area=self.area, base=True, team=True, decimals=True
        )
        self.record_level_area.types.add(self.competition.type)
        self.record_level_area.levels.add(self.competition.level)
        self.result = ResultFactory.create(
            competition=self.competition, athlete=self.athlete, category=self.category_W20, result=200
        )
        self.competition_result_type = CompetitionResultTypeFactory.create(
            competition_type=self.result.competition.type
        )
        self.object = Record.objects.all().first()
        self.data = {
            "result": self.object.result.id,
            "partial_result": None,
            "level": self.object.level.id,
            "type": self.object.type.id,
            "category": self.object.category.id,
            "approved": self.object.approved,
            "date_start": self.object.date_start.strftime("%Y-%m-%d"),
            "date_end": None,
            "info": self.object.info,
            "historical": self.object.historical,
        }
        self.newdata = {
            "result": self.object.result.id,
            "partial_result": None,
            "level": self.object.level.id,
            "type": self.object.type.id,
            "category": self.object.category.id,
            "approved": True,
            "date_start": self.object.date_start.strftime("%Y-%m-%d"),
            "date_end": None,
            "info": self.object.info,
            "historical": self.object.historical,
        }
        self.url = "/api/results/"
        self.viewset = RecordViewSet
        self.model = Record

    def _test_access(self, user):
        request = self.factory.get(self.url + "1/")
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"get": "retrieve"})
        return view(request, pk=self.object.pk)

    def _test_create(self, user, data):
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"post": "create"})
        return view(request)

    def _test_delete(self, user):
        request = self.factory.delete(self.url + "1/")
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"delete": "destroy"})
        return view(request, pk=1)

    def _test_update(self, user, data):
        request = self.factory.put(self.url + "1/", data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={"put": "update"})
        return view(request, pk=1)

    def test_record_creation(self):
        self.assertEqual(Record.objects.all().count(), 2)
        self.assertEqual(Record.objects.filter(approved=False).count(), 2)

    def test_record_creation_higher(self):
        self.model.objects.all().update(approved=True)
        ResultFactory.create(
            competition=self.competition, athlete=self.athlete_old, category=self.category_W, result=300
        )
        self.assertEqual(Record.objects.all().count(), 4)
        self.assertEqual(Record.objects.filter(approved=False).count(), 2)

    @override_settings(CREATE_RECORD_FOR_SAME_RESULT_VALUE=True)
    def test_record_creation_same_value_setting_true(self):
        self.model.objects.all().update(approved=True)
        ResultFactory.create(
            competition=self.competition_later, athlete=self.athlete2, category=self.category_W, result=200
        )
        self.assertEqual(Record.objects.all().count(), 4)
        self.assertEqual(Record.objects.filter(approved=False).count(), 2)

    @override_settings(CREATE_RECORD_FOR_SAME_RESULT_VALUE=False)
    def test_record_creation_same_value_setting_false(self):
        self.model.objects.all().update(approved=True)
        ResultFactory.create(
            competition=self.competition_later, athlete=self.athlete2, category=self.category_W, result=200
        )
        self.assertEqual(Record.objects.all().count(), 2)
        self.assertEqual(Record.objects.filter(approved=False).count(), 0)

    def test_record_creation_no_record_check(self):
        self.category_check.check_record = False
        self.category_check.save()
        ResultFactory.create(
            competition=self.competition, athlete=self.athlete_old, category=self.category_W, result=300
        )
        self.assertEqual(Record.objects.all().count(), 2)
        self.assertEqual(Record.objects.filter(approved=False).count(), 2)

    def test_record_creation_higher_area(self):
        self.model.objects.all().update(approved=True)
        self.athlete_old.organization.areas.add(self.area)
        ResultFactory.create(
            competition=self.competition,
            athlete=self.athlete_old,
            organization=self.athlete_old.organization,
            category=self.category_W,
            result=300,
        )
        self.assertEqual(Record.objects.all().count(), 6)
        self.assertEqual(Record.objects.filter(approved=False).count(), 4)

    def test_record_creation_lower(self):
        self.model.objects.all().update(approved=True)
        ResultFactory.create(
            competition=self.competition, athlete=self.athlete_old, category=self.category_W, result=150
        )
        self.assertEqual(Record.objects.all().count(), 3)
        self.assertEqual(Record.objects.filter(approved=False).count(), 1)

    def test_partial_record_creation(self):
        self.object = ResultPartialFactory.create(result=self.result, type=self.competition_result_type, value=50)
        self.assertEqual(Record.objects.exclude(partial_result=None).count(), 2)

    def test_partial_record_creation_no_partial_records_for_category(self):
        self.category_check_W20.check_record_partial = False
        self.category_check_W20.save()
        self.object = ResultPartialFactory.create(result=self.result, type=self.competition_result_type, value=50)
        self.assertEqual(Record.objects.exclude(partial_result=None).count(), 0)

    def test_partial_record_creation_limit_partial(self):
        self.category_check_W20.limit_partial.add(self.competition_result_type)
        self.object = ResultPartialFactory.create(result=self.result, type=self.competition_result_type, value=50)
        self.assertEqual(Record.objects.exclude(partial_result=None).count(), 0)

    @override_settings(CREATE_RECORD_FOR_SAME_RESULT_VALUE=False)
    def test_partial_record_creation_same_value_setting_false(self):
        self.object = ResultPartialFactory.create(result=self.result, type=self.competition_result_type, value=50)
        result = ResultFactory.create(
            competition=self.competition_later, athlete=self.athlete2, category=self.category_W20, result=200
        )
        self.model.objects.all().update(approved=True)
        self.object = ResultPartialFactory.create(result=result, type=self.competition_result_type, value=50)
        self.assertEqual(Record.objects.all().count(), 4)
        self.assertEqual(Record.objects.filter(approved=False).count(), 0)
        self.assertEqual(Record.objects.exclude(partial_result=None).count(), 2)

    @override_settings(CREATE_RECORD_FOR_SAME_RESULT_VALUE=True)
    def test_partial_record_creation_same_value_setting_true(self):
        result = ResultFactory.create(
            competition=self.competition_later, athlete=self.athlete2, category=self.category_W20, result=150
        )
        self.object = ResultPartialFactory.create(result=self.result, type=self.competition_result_type, value=50)
        self.model.objects.all().update(approved=True)
        self.object = ResultPartialFactory.create(result=result, type=self.competition_result_type, value=50)
        self.assertEqual(Record.objects.all().count(), 6)
        self.assertEqual(Record.objects.filter(approved=False).count(), 2)
        self.assertEqual(Record.objects.exclude(partial_result=None).count(), 4)

    def test_team_record_creation(self):
        self.model.objects.all().update(approved=True)
        ResultFactory.create(
            competition=self.competition, athlete=self.athlete_old, category=self.category_team, result=300, team=True
        )
        self.assertEqual(Record.objects.filter(category__team=True).count(), 1)
        self.assertEqual(Record.objects.filter(result__team=True).count(), 1)

    def test_record_approval_ending(self):
        self.model.objects.all().update(approved=True)
        ResultFactory.create(
            competition=self.competition, athlete=self.athlete_old, category=self.category_W, result=300
        )
        self.assertEqual(Record.objects.all().count(), 4)
        self.assertEqual(Record.objects.filter(approved=False).count(), 2)
        for record in self.model.objects.all():
            if not record.approved:
                record.approved = True
                record.save()
        self.assertEqual(Record.objects.all().count(), 4)
        self.assertEqual(Record.objects.filter(date_end=None).count(), 3)

    def test_record_approval_removal(self):
        result = ResultFactory.create(
            competition=self.competition, athlete=self.athlete_old, category=self.category_W, result=300
        )
        for record in self.model.objects.filter(result=result):
            if not record.approved:
                record.approved = True
                record.save()
        self.assertEqual(Record.objects.all().count(), 3)
        self.assertEqual(Record.objects.filter(date_end=None).count(), 3)

    def test_record_access_list(self):
        request = self.factory.get(self.url)
        view = self.viewset.as_view(actions={"get": "list"})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_record_access_object_without_user(self):
        response = self._test_access(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_record_access_object_with_normal_user(self):
        response = self._test_access(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_record_update_without_user(self):
        response = self._test_update(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_record_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_record_update_with_staffruser(self):
        response = self._test_update(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_record_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_area_approve(self, data=None):
        if data is None:
            data = {"approved": True}
        self.athlete.organization.areas.add(self.area)
        self.result = ResultFactory.create(
            competition=self.competition_later,
            athlete=self.athlete,
            category=self.category_W,
            result=150,
            organization=self.athlete.organization,
        )
        record = Record.objects.filter(level__area__isnull=False).first()
        request = self.factory.put(self.url + str(record.pk) + "/", data)
        force_authenticate(request, user=self.user)
        view = self.viewset.as_view(actions={"put": "partial_update"})
        record.refresh_from_db()
        return view(request, pk=record.pk)

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_record_approve_area_record_with_normal_user(self):
        response = self._test_area_approve()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Record.objects.filter(level__area__isnull=False).first().approved)

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_record_approve_area_record_with_area_manager(self):
        self.user.groups.add(self.area_group)
        response = self._test_area_approve()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Record.objects.filter(level__area__isnull=False).first().approved)

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_record_update_area_record_with_area_manager(self):
        self.user.groups.add(self.area_group)
        response = self._test_area_approve(data={"approved": True, "category": self.object.category.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "No permission to alter or create a record.")

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_record_approve_area_record_with_sport_manager(self):
        self.user.groups.add(self.object.result.competition.type.sport.manager)
        response = self._test_area_approve()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Record.objects.filter(level__area__isnull=False).first().approved)

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_record_update_area_record_with_sport_manager(self):
        self.user.groups.add(self.object.result.competition.type.sport.manager)
        response = self._test_area_approve(data={"approved": True, "category": self.object.category.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "No permission to alter or create a record.")

    def test_record_create_without_user(self):
        response = self._test_create(user=None, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_record_create_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 3)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_record_create_existing_with_superuser(self):
        response = self._test_create(user=self.superuser, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_record_create_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.all().count(), 3)
        for key in self.newdata:
            self.assertEqual(response.data[key], self.newdata[key])

    def test_record_create_existing_with_staffuser(self):
        response = self._test_create(user=self.staff_user, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_record_create_with_normal_user(self):
        response = self._test_create(user=self.user, data=self.newdata)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_record_delete_with_user(self):
        response = self._test_delete(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_record_delete_with_superuser(self):
        response = self._test_delete(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_record_delete_with_staffuser(self):
        response = self._test_delete(user=self.staff_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

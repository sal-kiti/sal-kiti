from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from results.models.competitions import Competition
from results.models.events import Event
from results.models.records import RecordLevel
from results.models.results import Result
from results.tests.factories.results import ResultFactory, ResultPartialFactory


class CreateEvent(TestCase):
    def test_command_output(self):
        self.user = User.objects.create(username="logger")
        call_command("createevent", "5", base_data=True, verbosity=0)
        self.assertEqual(Result.objects.count(), 36)
        self.assertEqual(Competition.objects.count(), 9)


class Approve(TestCase):
    def test_approve_no_objects_within_date_limit(self):
        self.user = User.objects.create(username="logger")
        ResultFactory.create(approved=False, competition__locked=False, competition__event__locked=False)
        call_command("approve", days=1, result=True, record=True, event=True, competition=True, verbosity=0)
        self.assertEqual(Result.objects.filter(approved=False).count(), 1)
        self.assertEqual(Event.objects.filter(locked=False).count(), 1)
        self.assertEqual(Competition.objects.filter(locked=False).count(), 1)

    def test_approve_objects_within_date_limit(self):
        self.user = User.objects.create(username="logger")
        result = ResultFactory.create(approved=False, competition__locked=False, competition__event__locked=False)
        call_command("approve", days=0, result=True, record=True, event=True, competition=True, verbosity=0)
        self.assertEqual(Result.objects.filter(approved=False).count(), 0)
        self.assertEqual(Event.objects.filter(locked=False).count(), 1)
        self.assertEqual(Competition.objects.filter(locked=False).count(), 1)
        result.competition.date_end = result.competition.date_start
        result.competition.save()
        result.competition.event.date_end = result.competition.event.date_start
        result.competition.event.save()
        call_command("approve", days=0, result=True, record=True, event=True, competition=True, verbosity=0)
        self.assertEqual(Event.objects.filter(locked=False).count(), 0)
        self.assertEqual(Competition.objects.filter(locked=False).count(), 0)

    def test_approve_unpublished_result(self):
        self.user = User.objects.create(username="logger")
        result = ResultFactory.create(
            approved=False, public=False, competition__locked=False, competition__event__locked=False
        )
        call_command("approve", days=0, result=True, verbosity=0)
        self.assertEqual(Result.objects.filter(approved=False).count(), 1)
        result.public = True
        result.save()
        call_command("approve", days=0, result=True, verbosity=0)
        self.assertEqual(Result.objects.filter(approved=False).count(), 0)


class TestRecordCheck(TestCase):
    def test_record_check_script(self):
        User.objects.create(username="logger")
        out = StringIO()
        result = ResultFactory.create()
        ResultPartialFactory(result=result)
        record_level = RecordLevel.objects.create(
            name="TEST", abbreviation="TEST", base=True, decimals=True, team=True
        )
        record_level_2 = RecordLevel.objects.create(
            name="TEST2", abbreviation="TEST2", base=True, decimals=True, team=True
        )
        record_level_partial = RecordLevel.objects.create(
            name="PARTIAL", abbreviation="PARTIAL", base=False, decimals=True, partial=True
        )
        record_level.types.add(result.competition.type)
        record_level_2.types.add(result.competition.type)
        record_level_partial.types.add(result.competition.type)
        record_level.levels.add(result.competition.level)
        record_level_2.levels.add(result.competition.level)
        record_level_partial.levels.add(result.competition.level)
        call_command("checkrecords", results=True, partial=True, stdout=out)
        self.assertIn(f"Created 2 record(s) for result {result.competition.date_start.isoformat()}", out.getvalue())
        self.assertIn("Created 1 record(s) for partial result", out.getvalue())
        out = StringIO()
        call_command(
            "checkrecords",
            results=True,
            date=result.competition.date_start.isoformat(),
            competition_levels=[result.competition.level.abbreviation],
            competition_types=[result.competition.type.abbreviation],
            stdout=out,
        )
        self.assertIn("Created 2 record(s) for result", out.getvalue())
        self.assertNotIn("Created 1 record(s) for partial result", out.getvalue())
        out = StringIO()
        call_command(
            "checkrecords",
            results=True,
            date=(result.competition.date_start + timedelta(days=1)).isoformat(),
            stdout=out,
        )
        self.assertEqual("", out.getvalue())
        out = StringIO()
        call_command(
            "checkrecords",
            results=True,
            sports=["invalid"],
            stdout=out,
        )
        self.assertEqual("", out.getvalue())

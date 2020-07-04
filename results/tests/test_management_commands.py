from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from results.models.competitions import Competition
from results.models.events import Event
from results.models.results import Result
from results.tests.factories.results import ResultFactory


class CreateEvent(TestCase):
    def test_command_output(self):
        self.user = User.objects.create(username='logger')
        call_command('createevent', '5', base_data=True, verbosity=0)
        self.assertEqual(Result.objects.count(), 36)
        self.assertEqual(Competition.objects.count(), 9)


class Approve(TestCase):
    def test_approve_no_objects_within_date_limit(self):
        self.user = User.objects.create(username='logger')
        ResultFactory.create(approved=False, competition__locked=False, competition__event__locked=False)
        call_command('approve', days=1, result=True, record=True, event=True, competition=True, verbosity=0)
        self.assertEqual(Result.objects.filter(approved=False).count(), 1)
        self.assertEqual(Event.objects.filter(locked=False).count(), 1)
        self.assertEqual(Competition.objects.filter(locked=False).count(), 1)

    def test_approve_objects_within_date_limit(self):
        self.user = User.objects.create(username='logger')
        ResultFactory.create(approved=False, competition__locked=False, competition__event__locked=False)
        call_command('approve', days=0, result=True, record=True, event=True, competition=True, verbosity=0)
        self.assertEqual(Result.objects.filter(approved=False).count(), 0)
        self.assertEqual(Event.objects.filter(locked=False).count(), 0)
        self.assertEqual(Competition.objects.filter(locked=False).count(), 0)

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from results.models.competitions import Competition
from results.models.results import Result


class CreateEvent(TestCase):
    def test_command_output(self):
        self.user = User.objects.create(username='logger')
        call_command('createevent', '5', base_data=True, verbosity=0)
        self.assertEqual(Result.objects.count(), 36)
        self.assertEqual(Competition.objects.count(), 9)

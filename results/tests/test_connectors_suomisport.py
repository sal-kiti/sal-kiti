import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from results.connectors.suomisport import Suomisport
from results.models.athletes import Athlete
from results.tests.factories.athletes import AthleteFactory
from results.tests.factories.organizations import OrganizationFactory


class OAuth(object):
    def __init__(self, url):
        self.url = url

    def json(self):
        today = datetime.date.today().isoformat()
        if self.url.startswith('licence'):
            return {
                "content": [
                    {
                        "id": 5,
                        "type": "Competition",
                        "usageEndTime": "2020-01-01",
                        "usageStartTime": "2020-01-01",
                        "licencePeriodId": 1,
                    },
                    {
                        "id": 5,
                        "type": "Competition",
                        "usageEndTime": today,
                        "usageStartTime": today,
                        "licencePeriodId": 2,
                    }
                ]
            }
        if self.url.startswith('user-lic'):
            if 'page=0' in self.url:
                return {
                    "content": [
                        {
                            "licenceOrganizationSportId": 1,
                            "usagePeriodEnd": today,
                            "usagePeriodStart": today,
                            "name": "Competition licence",
                            "modificationTime": "2020-01-01T12:00:01.123Z",
                            "user": {
                                "birthDate": "1990-03-01",
                                "firstName": "MattiAB",
                                "gender": "Male",
                                "lastName": "Meikäläinen",
                                "sportId": 123456789
                            }
                        }
                    ],
                    "pageable": {
                        "page": 0,
                        "size": 1,
                        "total": 2
                    }
                }
            else:
                return {
                    "content": [
                        {
                            "licenceOrganizationSportId": 1,
                            "usagePeriodEnd": today,
                            "usagePeriodStart": today,
                            "name": "Competition licence",
                            "modificationTime": "2020-01-01T12:00:01.123Z",
                            "user": {
                                "birthDate": "1980-03-01",
                                "firstName": "Maija",
                                "nickname": "Maju ",
                                "gender": "Female",
                                "lastName": "AINA-MEIKÄLÄINEN",
                                "sportId": 987654321
                            }
                        }
                    ],
                    "pageable": {
                        "page": 1,
                        "size": 2,
                        "total": 2
                    }
                }
        return {}


class TestSuomiSport(Suomisport):

    def __init__(self):
        self.base_url = ''
        self.organization_id = '1'
        self.licence_types = ['Competition']
        self.fetch_size = 1
        self.oauth = OAuth
        self.oauth.get = OAuth


class SuomisportCase(TestCase):
    def test_get_licence_types(self):
        obj = TestSuomiSport()
        result = obj.get_licence_types()
        self.assertEqual(result[0]['id'], 5)

    def test_get_licences(self):
        obj = TestSuomiSport()
        result = obj.get_licences(1, 1)
        self.assertEqual(len(result), 2)

    @patch('results.connectors.suomisport.logger')
    def test_update_licences(self, mock_logger):
        User.objects.create_user('log')
        OrganizationFactory.create(sport_id=1)
        AthleteFactory.create(sport_id='123456789')
        obj = TestSuomiSport()
        obj.update_licences(update_only_latest=True, print_to_stdout=False)
        mock_logger.info.assert_called_with('Created new athlete from Suomisport: %s', '987654321')
        self.assertEqual(Athlete.objects.count(), 2)
        self.assertEqual(Athlete.objects.get(id=1).first_name, 'Mattiab')
        self.assertEqual(Athlete.objects.get(id=2).gender, 'W')
        self.assertEqual(Athlete.objects.get(id=2).first_name, 'Maju')
        self.assertEqual(Athlete.objects.get(id=2).last_name, 'Aina-Meikäläinen')

    def test_ignore_athlete_updates(self):
        User.objects.create_user('log')
        OrganizationFactory.create(sport_id=1)
        athlete = AthleteFactory.create(sport_id='123456789', no_auto_update=True)
        name = athlete.last_name
        obj = TestSuomiSport()
        obj.update_licences(update_only_latest=True, print_to_stdout=False)
        self.assertNotEqual(Athlete.objects.get(id=1).first_name, 'Mattiab')
        self.assertEqual(Athlete.objects.get(id=1).last_name, name)

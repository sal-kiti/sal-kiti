import datetime
import logging
from sys import stdout

from dateutil.parser import isoparse
from django.conf import settings
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from results.models.athletes import Athlete, AthleteInformation
from results.models.organizations import Organization

logger = logging.getLogger(__name__)


class Suomisport:
    """
    Connector for updating athlete and licence information from Suomisport
    API description: https://info.suomisport.fi/wp-content/uploads/2020/01/suomisport-API.html
    """

    def __init__(self):
        """
        Initialize connection and set setting values.
        """
        client_id = settings.SUOMISPORT.get("CLIENT_ID", None)
        client_secret = settings.SUOMISPORT.get("CLIENT_SECRET", None)
        self.token_url = settings.SUOMISPORT.get("TOKEN_URL", None)
        self.base_url = settings.SUOMISPORT.get("BASE_URL", None)
        self.organization_id = settings.SUOMISPORT.get("ORGANIZATION_ID", None)
        self.licence_types = settings.SUOMISPORT.get("LICENCE_TYPES", None)
        self.fetch_size = settings.SUOMISPORT.get("FETCH_SIZE", 1000)
        auth = HTTPBasicAuth(client_id, client_secret)
        client = BackendApplicationClient(client_id=client_id)
        self.oauth = OAuth2Session(client=client)
        self.token = self.oauth.fetch_token(token_url=self.token_url, auth=auth)

    def _fetch_from_api(self, path, ts=None):
        """
        Fetch information from API. Creates multiple requests if all results do not fit in FETCH_SIZE parameter.

        :param path: path to resource, i.e. 'licence/'
        :param ts: fetch only results updates since ts
        :type path: str
        :type ts: datetime
        :return: content list
        :rtype: list
        """
        content = []
        page = 0
        while True:
            url = self.base_url + path + "?page=" + str(page) + "&size=" + str(self.fetch_size)
            if ts:
                url += "&ts=" + ts.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            result = self.oauth.get(url).json()
            if not result or "content" not in result:
                break
            content += result["content"]
            if (
                "pageable" not in result
                or result["pageable"]["total"] < result["pageable"]["size"]
                or (page > 0 and result["pageable"]["total"] < result["pageable"]["size"] * (page + 1))
            ):
                break
            page += 1
        return content

    def get_licence_types(self, date=None):
        """
        Get licence types.

        :param date: Include only licence types active during this date
        :type date: date
        :return: licence types
        :rtype: list
        """
        url = "licence/" + self.organization_id
        licence_types = self._fetch_from_api(url)
        result = []
        for licence_type in licence_types:
            start = datetime.datetime.strptime(licence_type["usageStartTime"], "%Y-%m-%d").date()
            end = datetime.datetime.strptime(licence_type["usageEndTime"], "%Y-%m-%d").date()
            if date is None or start <= date <= end:
                result.append(licence_type)
        return result

    def get_licences(self, licence_period_id, licence_type_id, ts=None):
        """
        Get licences

        :param licence_period_id: licence period id
        :param licence_type_id: licence type id
        :param ts: fetch only results updates since ts
        :param licence_period_id: int
        :param licence_type_id: int
        :param ts: datetime
        :return: licences
        :rtype: list
        """
        url = "user-licence/" + self.organization_id + "/" + str(licence_period_id) + "/" + str(licence_type_id)
        licences = self._fetch_from_api(url, ts)
        return licences

    @staticmethod
    def _parse_gender(gender):
        """
        Parse Kiti gender from Suomisport gender

        :param gender: Gender in Suomisport
        :type gender: str
        :return: gender in Kiti single character format
        :rtype: str
        """
        if gender == "Female":
            return "W"
        if gender == "Male":
            return "M"
        if gender == "Both":
            return "O"
        else:
            return "U"

    @staticmethod
    def _capitalize_name(name):
        parts = name.split("-")
        for index, part in enumerate(parts):
            parts[index] = part.strip().capitalize()
        return "-".join(parts)

    def _update_athletes(self, licences, print_to_stdout=False, only_year=False):
        """
        Update athletes and licences based on Suomisport licence list

        :param licences: Suomisport licence list
        :param print_to_stdout: print messages to stdout
        :type licences: list
        :type print_to_stdout: bool
        """
        for licence in licences:
            try:
                organization = Organization.objects.get(sport_id=str(licence["licenceOrganizationSportId"]))
            except Organization.DoesNotExist:
                logger.warning("Could not find organization with ID: %s", str(licence["licenceOrganizationSportId"]))
                if print_to_stdout:
                    stdout.write(
                        "Could not find organization with ID: %s\n" % str(licence["licenceOrganizationSportId"])
                    )
                continue
            start = datetime.datetime.strptime(licence["usagePeriodStart"], "%Y-%m-%d").date()
            end = datetime.datetime.strptime(licence["usagePeriodEnd"], "%Y-%m-%d").date()
            licence_name = licence["name"]
            modification_time = isoparse(licence["modificationTime"])
            user = licence["user"]
            sport_id = str(user["sportId"])
            first_name = self._capitalize_name(user["nickname"]) if "nickname" in user else None
            if not first_name:
                first_name = self._capitalize_name(user["firstName"].split(" ")[0])
            last_name = self._capitalize_name(user["lastName"])
            gender = self._parse_gender(user["gender"])
            date_of_birth = datetime.datetime.strptime(user["birthDate"], "%Y-%m-%d").date()
            if only_year:
                date_of_birth = date_of_birth.replace(month=1, day=1)
            try:
                athlete = Athlete.objects.get(sport_id=sport_id)
                modified = False
                if athlete.first_name != first_name:
                    athlete.first_name = first_name
                    modified = True
                if athlete.last_name != last_name:
                    athlete.last_name = last_name
                    modified = True
                if athlete.gender != gender:
                    athlete.gender = gender
                    modified = True
                if athlete.date_of_birth != date_of_birth:
                    athlete.date_of_birth = date_of_birth
                    modified = True
                if not athlete.organization or athlete.organization != organization:
                    athlete.organization = organization
                    modified = True
                if modified:
                    if not athlete.no_auto_update:
                        athlete.save()
                        logger.info("Updated athlete information from Suomisport: %s", sport_id)
                        if print_to_stdout:
                            stdout.write("Modified athlete: %s\n" % sport_id)
                    else:
                        if print_to_stdout:
                            stdout.write("Athlete update prevented by no_auto_update: %s\n" % sport_id)
            except Athlete.DoesNotExist:
                athlete = Athlete.objects.create(
                    sport_id=sport_id,
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    organization=organization,
                )
                logger.info("Created new athlete from Suomisport: %s", sport_id)
                if print_to_stdout:
                    stdout.write("Created athlete: %s\n" % sport_id)
            AthleteInformation.objects.get_or_create(
                athlete=athlete,
                type="licence",
                value=licence_name,
                date_start=start,
                date_end=end,
                modification_time=modification_time,
                visibility="A",
            )

    def update_licences(self, update_only_latest=True, print_to_stdout=False, only_year=False):
        """
        Fetch licences and update athletes

        :param update_only_latest: update only licences added since last modification time
        :param print_to_stdout: print messages to stdout
        :param only_year: set athlete's birth date to YYYY-01-01
        :type update_only_latest: bool
        :type print_to_stdout: bool
        :type only_year: bool
        """
        if update_only_latest:
            try:
                latest_modification = (
                    AthleteInformation.objects.filter(type="licence", modification_time__isnull=False)
                    .latest("modification_time")
                    .modification_time
                )
            except AthleteInformation.DoesNotExist:
                latest_modification = None
        else:
            latest_modification = None
        licence_types = self.get_licence_types(datetime.date.today())
        for licence_type in licence_types:
            if "type" in licence_type:
                if licence_type["type"] in self.licence_types:
                    licences = self.get_licences(
                        licence_type["licencePeriodId"], licence_type["id"], ts=latest_modification
                    )
                    self._update_athletes(licences=licences, print_to_stdout=print_to_stdout, only_year=only_year)
            else:
                if print_to_stdout:
                    stdout.write("%s: %s\n" % ("WARNING: Licence type does not include type attribute", licence_type))

    def get_organizations(self, print_to_stdout=False):
        """
        Fetch licences and update athletes

        :param print_to_stdout: print messages to stdout
        :type print_to_stdout: bool
        """
        url = "organization/" + self.organization_id + "/list"
        organizations = self._fetch_from_api(url)
        for item in organizations:
            sport_id = item["sportId"]
            name = item["name"]
            if "shortName" in item and item["shortName"]:
                abbreviation = item["shortName"]
            else:
                abbreviation = None
            organization = Organization.objects.none()
            if abbreviation:
                organization = Organization.objects.filter(abbreviation__iexact=abbreviation)
            if organization.count() != 1:
                organization = Organization.objects.filter(name__iexact=name)
            if print_to_stdout:
                if organization.count() == 1:
                    stdout.write("%s;%s;%s;%s\n" % ("FOUND", organization[0].abbreviation, sport_id, name))
                else:
                    stdout.write("%s;%s;%s;%s\n" % ("NOT FOUND", sport_id, name, abbreviation))

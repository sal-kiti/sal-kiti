from rest_framework import routers

from results.views.athletes import AthleteInformationViewSet, AthleteViewSet
from results.views.categories import CategoryViewSet, DivisionViewSet
from results.views.competitions import (
    CompetitionLayoutViewSet,
    CompetitionLevelViewSet,
    CompetitionResultTypeViewSet,
    CompetitionTypeViewSet,
    CompetitionViewSet,
)
from results.views.events import EventContactViewSet, EventViewSet
from results.views.organizations import AreaViewSet, OrganizationViewSet
from results.views.records import RecordLevelViewSet, RecordList, RecordViewSet
from results.views.results import (
    ResultDetailViewSet,
    ResultList,
    ResultPartialViewSet,
    ResultViewSet,
)
from results.views.sports import SportViewSet
from results.views.statistics import StatisticsLinkViewSet

router = routers.DefaultRouter()
router.register(r"areas", AreaViewSet)
router.register(r"athletes", AthleteViewSet)
router.register(r"athleteinformation", AthleteInformationViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"divisions", DivisionViewSet)
router.register(r"competitions", CompetitionViewSet)
router.register(r"events", EventViewSet)
router.register(r"eventcontacts", EventContactViewSet)
router.register(r"competitionlevels", CompetitionLevelViewSet)
router.register(r"competitiontypes", CompetitionTypeViewSet)
router.register(r"competitionlayouts", CompetitionLayoutViewSet)
router.register(r"competitionresulttypes", CompetitionResultTypeViewSet)
router.register(r"organizations", OrganizationViewSet)
router.register(r"records", RecordViewSet)
router.register(r"recordlevels", RecordLevelViewSet)
router.register(r"recordlist", RecordList)
router.register(r"results", ResultViewSet)
router.register(r"partialresults", ResultPartialViewSet)
router.register(r"resultdetail", ResultDetailViewSet)
router.register(r"resultlist", ResultList)
router.register(r"sports", SportViewSet)
router.register(r"statisticslinks", StatisticsLinkViewSet)

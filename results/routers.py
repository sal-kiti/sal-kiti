from rest_framework import routers

from results.views.athletes import AthleteViewSet, AthleteInformationViewSet
from results.views.categories import CategoryViewSet, DivisionViewSet
from results.views.competitions import CompetitionViewSet, CompetitionLevelViewSet, CompetitionTypeViewSet
from results.views.competitions import CompetitionResultTypeViewSet, CompetitionLayoutViewSet
from results.views.events import EventViewSet
from results.views.organizations import AreaViewSet, OrganizationViewSet
from results.views.records import RecordViewSet, RecordLevelViewSet, RecordList
from results.views.results import ResultViewSet, ResultPartialViewSet, ResultDetailViewSet
from results.views.results import ResultList
from results.views.sports import SportViewSet

router = routers.DefaultRouter()
router.register(r'areas', AreaViewSet)
router.register(r'athletes', AthleteViewSet)
router.register(r'athleteinformation', AthleteInformationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'divisions', DivisionViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'events', EventViewSet)
router.register(r'competitionlevels', CompetitionLevelViewSet)
router.register(r'competitiontypes', CompetitionTypeViewSet)
router.register(r'competitionlayouts', CompetitionLayoutViewSet)
router.register(r'competitionresulttypes', CompetitionResultTypeViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'records', RecordViewSet)
router.register(r'recordlevels', RecordLevelViewSet)
router.register(r'recordlist', RecordList)
router.register(r'results', ResultViewSet)
router.register(r'partialresults', ResultPartialViewSet)
router.register(r'resultdetail', ResultDetailViewSet)
router.register(r'resultlist', ResultList)
router.register(r'sports', SportViewSet)

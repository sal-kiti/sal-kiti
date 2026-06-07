from rest_framework import routers

from divari.views import (
    CompetitionViewSet,
    ResultViewSet,
    SeasonResultViewSet,
    SeasonViewSet,
    TeamViewSet,
)

router = routers.DefaultRouter()
router.register(r"competitions", CompetitionViewSet)
router.register(r"results", ResultViewSet)
router.register(r"seasons", SeasonViewSet)
router.register(r"seasonresults", SeasonResultViewSet)
router.register(r"teams", TeamViewSet)

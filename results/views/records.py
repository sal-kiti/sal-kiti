from django.db.models import Prefetch
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import mixins, viewsets

from results.models.athletes import AthleteInformation
from results.models.records import Record, RecordLevel
from results.serializers.records import RecordLevelSerializer, RecordSerializer
from results.serializers.records_list import RecordListSerializer


class RecordViewSet(viewsets.ModelViewSet):
    """API endpoint for records.

    list:
    Returns a list of all the existing records.

    retrieve:
    Returns the given record.

    create:
    Creates a new record instance.

    update:
    Updates a given record.

    partial_update:
    Updates a given record.

    destroy:
    Removes the given record.
    """

    permission_classes = (DRYPermissions,)
    queryset = Record.objects.all()
    serializer_class = RecordSerializer


class RecordLevelViewSet(viewsets.ModelViewSet):
    """API endpoint for record levels.

    list:
    Returns a list of all the existing record levels.

    retrieve:
    Returns the given record level.

    create:
    Creates a new record level instance.

    update:
    Updates a given record level.

    partial_update:
    Updates a given record level.

    destroy:
    Removes the given record level.
    """

    permission_classes = (DRYPermissions,)
    queryset = RecordLevel.objects.all()
    serializer_class = RecordLevelSerializer

    def get_queryset(self):
        """
        Setup eager loading of linked models
        """
        self.queryset = self.get_serializer_class().setup_eager_loading(self.queryset)
        return self.queryset


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class RecordListFilter(filters.FilterSet):
    """
    Filters for RecordList view.
    """

    category = NumberInFilter(field_name="category__pk", lookup_expr="in")
    level = NumberInFilter(field_name="level__pk", lookup_expr="in")
    type = NumberInFilter(field_name="type__pk", lookup_expr="in")
    sport = NumberInFilter(field_name="type__sport__pk", lookup_expr="in")
    historical = filters.BooleanFilter(field_name="historical", widget=BooleanWidget())
    approved = filters.BooleanFilter(field_name="approved", widget=BooleanWidget())
    start = filters.DateFilter(field_name="date_start", lookup_expr="gte")
    end = filters.DateFilter(field_name="date_end", lookup_expr="lte")

    o = filters.OrderingFilter(
        fields=(
            ("type", "type"),
            ("category", "category"),
            ("approved", "approved"),
            ("level", "level"),
        )
    )


class RecordList(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint for retrieving record list.

    retrieve:
    Returns the record list, filtered by fields.
    """

    permission_classes = (DRYPermissions,)
    queryset = Record.objects.filter(date_end=None)
    serializer_class = RecordListSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecordListFilter

    def get_queryset(self):
        """
        Setup eager loading of linked models
        """
        athlete_information_queryset = AthleteInformation.get_visibility_queryset(
            user=self.request.user, queryset=AthleteInformation.objects.all()
        )
        prefetch = [
            Prefetch("result__athlete__info", queryset=athlete_information_queryset),
            Prefetch("result__team_members__info", queryset=athlete_information_queryset),
        ]
        self.queryset = self.get_serializer_class().setup_eager_loading(self.queryset, prefetch=prefetch)
        return self.queryset

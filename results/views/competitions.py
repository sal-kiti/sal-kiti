from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie

from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from results.models.competitions import Competition, CompetitionLevel, CompetitionType, CompetitionResultType
from results.models.competitions import CompetitionLayout
from results.serializers.competitions import CompetitionSerializer, CompetitionLevelSerializer
from results.serializers.competitions import CompetitionTypeSerializer, CompetitionResultTypeSerializer
from results.serializers.competitions import CompetitionLayoutSerializer
from results.utils.pagination import CustomPagePagination


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class CompetitionFilter(filters.FilterSet):
    """
    Custom filters for a competition.
    """
    level = NumberInFilter(field_name='level__pk', lookup_expr='in')
    type = NumberInFilter(field_name='type__pk', lookup_expr='in')
    sport = NumberInFilter(field_name='type__sport__pk', lookup_expr='in')
    start = filters.DateFilter(field_name='date_start', lookup_expr='gte')
    end = filters.DateFilter(field_name='date_end', lookup_expr='lte')

    class Meta:
        model = Competition
        fields = ['end', 'event', 'level', 'organization', 'public', 'sport', 'start', 'trial', 'type', 'approved']


class CompetitionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for competitions.

    list:
    Returns a list of all the existing competitions.

    retrieve:
    Returns the given competition.

    create:
    Creates a new competition instance.

    update:
    Updates a given competition.

    partial_update:
    Updates a given competition.

    destroy:
    Removes the given competition.
    """
    permission_classes = (DRYPermissions,)
    pagination_class = CustomPagePagination
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [filters.DjangoFilterBackend,
                       SearchFilter]
    filterset_class = CompetitionFilter
    search_fields = ('name', 'organization__name', 'organization__abbreviation')

    def get_queryset(self):
        """
        Restricts the returned information to public competitions, unless user is
        staff or superuser or user is representing the organizer of the competition.
        """
        user = self.request.user
        if settings.LIMIT_NON_PUBLIC_EVENT_AND_COMPETITION == "staff":
            if not user.is_superuser and not user.is_staff:
                self.queryset = self.queryset.filter(Q(public=True) | Q(organization__group__in=user.groups.all()))
        elif settings.LIMIT_NON_PUBLIC_EVENT_AND_COMPETITION == "authenticated":
            if not user.is_authenticated:
                self.queryset = self.queryset.filter(public=True)
        self.queryset = self.get_serializer_class().setup_eager_loading(self.queryset)
        return self.queryset

    @method_decorator(vary_on_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CompetitionLevelViewSet(viewsets.ModelViewSet):
    """API endpoint for competition levels.

    list:
    Returns a list of all the existing competition levels.

    retrieve:
    Returns the given competition level.

    create:
    Creates a new competition level instance.

    update:
    Updates a given competition level.

    partial_update:
    Updates a given competition level.

    destroy:
    Removes the given competition level.
    """
    permission_classes = (DRYPermissions,)
    queryset = CompetitionLevel.objects.all()
    serializer_class = CompetitionLevelSerializer


class CompetitionTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for competition types.

    list:
    Returns a list of all the existing competition types.

    retrieve:
    Returns the given competition type.

    create:
    Creates a new competition type instance.

    update:
    Updates a given competition type.

    partial_update:
    Updates a given competition type.

    destroy:
    Removes the given competition type.
    """
    permission_classes = (DRYPermissions,)
    queryset = CompetitionType.objects.all()
    serializer_class = CompetitionTypeSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['sport']


class CompetitionLayoutViewSet(viewsets.ModelViewSet):
    """API endpoint for competition layouts.

    list:
    Returns a list of all the existing competition layouts.

    retrieve:
    Returns the given competition layout.

    create:
    Creates a new competition layout instance.

    update:
    Updates a given competition layout.

    partial_update:
    Updates a given competition layout.

    destroy:
    Removes the given competition layout.
    """
    permission_classes = (DRYPermissions,)
    queryset = CompetitionLayout.objects.all()
    serializer_class = CompetitionLayoutSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['type']


class CompetitionResultTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for competition result types.

    list:
    Returns a list of all the existing competition result types.

    retrieve:
    Returns the given competition result type.

    create:
    Creates a new competition result type instance.

    update:
    Updates a given competition result type.

    partial_update:
    Updates a given competition result type.

    destroy:
    Removes the given competition result type.
    """
    permission_classes = (DRYPermissions,)
    queryset = CompetitionResultType.objects.all()
    serializer_class = CompetitionResultTypeSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['competition_type']

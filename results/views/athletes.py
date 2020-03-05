from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import filters, viewsets

from results.models.athletes import Athlete, AthleteInformation
from results.serializers.athletes import AthleteSerializer, AthleteLimitedSerializer, AthleteInformationSerializer
from results.utils.pagination import CustomPagePagination


class AthleteViewSet(viewsets.ModelViewSet):
    """API endpoint for athletes.

    Model: :class:`..models.athletes.Athlete`

    Date of birth and gender are only available for staff of superusers. They are also masked for everyone
    not in UNMASKED_ATHLETE_USERS settings group, except in POST requests.

    Creation of athletes in external organizations is allowed for any logged in user.

    list:
    Returns a list of all the existing athletes.

    retrieve:
    Returns the given athlete.

    create:
    Creates a new athlete instance.

    update:
    Updates a given athlete.

    partial_update:
    Updates a given athlete.

    destroy:
    Removes the given athlete.
    """
    permission_classes = (DRYPermissions,)
    pagination_class = CustomPagePagination
    queryset = Athlete.objects.all().order_by('sport_id')
    serializer_class = AthleteSerializer
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend]
    search_fields = ('first_name', 'last_name', 'sport_id')
    filterset_fields = ['sport_id', 'first_name', 'last_name']

    def get_serializer_class(self):
        """
        Returns limited information unless user is staff or superuser.
        """
        if self.request and (self.request.user.is_staff or self.request.user.is_superuser):
            return AthleteSerializer
        return AthleteLimitedSerializer

    @method_decorator(vary_on_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AthleteInformationViewSet(viewsets.ModelViewSet):
    """API endpoint for athlete information.

    Only public information is available for users without staff or superuser status.

    list:
    Returns a list of all the existing athletes information.

    retrieve:
    Returns the given athlete information.

    create:
    Creates a new athlete information instance.

    update:
    Updates a given athlete information.

    partial_update:
    Updates a given athlete information.

    destroy:
    Removes the given athlete information.
    """
    permission_classes = (DRYPermissions,)
    queryset = AthleteInformation.objects.all()
    serializer_class = AthleteInformationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['athlete']

    def get_queryset(self):
        """
        Restricts the returned information to public values, unless user is
        staff or superuser.
        """
        if not self.request or not self.request.user.is_authenticated:
            return self.queryset.filter(visibility='P')
        elif not (self.request.user.is_staff or self.request.user.is_superuser):
            return self.queryset.filter(visibility__in=['P', 'A'])
        elif not self.request.user.is_superuser:
            return self.queryset.filter(visibility__in=['P', 'A', 'S'])
        return self.queryset

    @method_decorator(vary_on_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

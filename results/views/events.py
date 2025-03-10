from django.conf import settings
from django.db.models import Prefetch, Q
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie
from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from results.models.athletes import AthleteInformation
from results.models.events import Event, EventContact
from results.serializers.events import EventContactSerializer, EventSerializer
from results.utils.pagination import CustomPagePagination


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class EventFilter(filters.FilterSet):
    """
    Custom filters for the event.
    """

    level = NumberInFilter(field_name="competitions__level__pk", lookup_expr="in")
    type = NumberInFilter(field_name="competitions__type__pk", lookup_expr="in")
    sport = NumberInFilter(field_name="competitions__type__sport__pk", lookup_expr="in")
    until = filters.DateFilter(field_name="date_start", lookup_expr="lte")
    start = filters.DateFilter(field_name="date_start", lookup_expr="gte")
    end = filters.DateFilter(field_name="date_end", lookup_expr="lte")

    class Meta:
        model = Event
        fields = ["level", "name", "organization", "public", "sport", "type", "approved"]


class EventViewSet(viewsets.ModelViewSet):
    """API endpoint for events.

    list:
    Returns a list of all the existing events.

    retrieve:
    Returns the given event.

    create:
    Creates a new event instance.

    update:
    Updates a given event.

    partial_update:
    Updates a given event.

    destroy:
    Removes the given event.
    """

    pagination_class = CustomPagePagination
    permission_classes = (DRYPermissions,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = EventFilter
    ordering_fields = ["date_start", "name"]
    search_fields = ("name", "organization__name", "organization__abbreviation")
    include_competitions = False

    def get_queryset(self):
        """
        Restricts the returned information to public events, unless user is
        staff or superuser or user is representing the organizer of the event.
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

    def partial_update(self, request, *args, **kwargs):
        self.include_competitions = request.data.get("include_competitions", False)
        return super().partial_update(request, *args, **kwargs)

    def _update_competitions(self, param, serializer):
        for competition in serializer.instance.competitions.all():
            if getattr(competition, param) != serializer.initial_data[param]:
                setattr(competition, param, serializer.initial_data[param])
                competition.save()

    def perform_update(self, serializer):
        if self.include_competitions:
            for param in ["public", "locked", "approved"]:
                if (
                    serializer.initial_data
                    and param in serializer.initial_data
                    and serializer.initial_data[param] != getattr(serializer.instance, param)
                ):
                    self._update_competitions(param, serializer)
        elif (
            settings.REMOVE_COMPETITION_APPROVAL_WITH_EVENT
            and serializer.instance.approved
            and "approved" in serializer.validated_data
            and not serializer.validated_data["approved"]
        ):
            self._update_competitions("approved", serializer)
        elif (
            settings.APPROVE_COMPETITIONS_WITH_EVENT
            and not serializer.instance.approved
            and "approved" in serializer.validated_data
            and serializer.validated_data["approved"]
        ):
            self._update_competitions("approved", serializer)
        serializer.save()


class EventContactViewSet(viewsets.ModelViewSet):
    """API endpoint for event contacts.

    list:
    Returns a list of all the existing event contacts.

    retrieve:
    Returns the given event contact.

    create:
    Creates a new event contact instance.

    update:
    Updates a given event contact.

    partial_update:
    Updates a given event contact.

    destroy:
    Removes the given event contact.
    """

    permission_classes = (DRYPermissions,)
    queryset = EventContact.objects.all()
    serializer_class = EventContactSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["event", "type", "athlete"]

    def get_queryset(self):
        """
        Restricts the returned information to the organizer of the event, unless user is
        staff or superuser.
        """
        user = self.request.user
        if not user.is_superuser and not user.is_staff:
            self.queryset = self.queryset.filter(Q(event__organization__group__in=user.groups.all()))
        athlete_information_queryset = AthleteInformation.get_visibility_queryset(
            user=self.request.user, queryset=AthleteInformation.objects.all()
        )
        prefetch = [
            Prefetch("athlete__info", queryset=athlete_information_queryset),
        ]
        self.queryset = self.get_serializer_class().setup_eager_loading(self.queryset, prefetch=prefetch)
        return self.queryset

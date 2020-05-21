from django.db.models import Q
from django_filters import rest_framework as filters
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets

from results.models.events import Event, EventContact
from results.serializers.events import EventSerializer, EventContactSerializer
from results.utils.pagination import CustomPagePagination


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class EventFilter(filters.FilterSet):
    """
    Custom filters for the event.
    """
    level = NumberInFilter(field_name='competition__level__pk', lookup_expr='in')
    type = NumberInFilter(field_name="competition__type__pk", lookup_expr='in')
    sport = NumberInFilter(field_name="competition__type__sport__pk", lookup_expr='in')
    until = filters.DateFilter(field_name='date_start', lookup_expr='lte')
    start = filters.DateFilter(field_name='date_start', lookup_expr='gte')
    end = filters.DateFilter(field_name='date_end', lookup_expr='lte')

    class Meta:
        model = Event
        fields = ['level', 'organization', 'public', 'sport', 'type']


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
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EventFilter

    def get_queryset(self):
        """
        Restricts the returned information to public events, unless user is
        staff or superuser or user is representing the organizer of the event.
        """
        user = self.request.user
        if not user.is_superuser and not user.is_staff:
            self.queryset = self.queryset.filter(Q(public=True) | Q(organization__group__in=user.groups.all()))
        self.queryset = self.get_serializer_class().setup_eager_loading(self.queryset)
        return self.queryset

    @method_decorator(vary_on_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


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

    def get_queryset(self):
        """
        Restricts the returned information to the organizer of the event, unless user is
        staff or superuser.
        """
        user = self.request.user
        if not user.is_superuser and not user.is_staff:
            self.queryset = self.queryset.filter(Q(event__organization__group__in=user.groups.all()))
        return self.queryset

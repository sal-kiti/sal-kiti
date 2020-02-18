from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets

from results.models.organizations import Area, Organization
from results.serializers.organizations import AreaSerializer, OrganizationSerializer


class AreaViewSet(viewsets.ModelViewSet):
    """API endpoint for organizational areas.

    list:
    Returns a list of all the existing areas.

    retrieve:
    Returns the given area.

    create:
    Creates a new area instance.

    update:
    Updates a given area.

    partial_update:
    Updates a given area.

    destroy:
    Removes the given area.
    """
    permission_classes = (DRYPermissions,)
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """API endpoint for organizations.

    list:
    Returns a list of all the existing organizations.

    retrieve:
    Returns the given organization.

    create:
    Creates a new organization instance.

    update:
    Updates a given organization.

    partial_update:
    Updates a given organization.

    destroy:
    Removes the given organization.
    """
    permission_classes = (DRYPermissions,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        """
        Optionally restricts returned results to user's managed organizations.
        """
        limit = self.request.query_params.get('limit', None)
        if limit and limit == "own":
            user = self.request.user
            if not user.is_superuser and not user.is_staff:
                self.queryset = self.queryset.filter(group__in=user.groups.all())
            self.pagination_class = None
        self.queryset = self.get_serializer_class().setup_eager_loading(self.queryset)
        return self.queryset

    @method_decorator(vary_on_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

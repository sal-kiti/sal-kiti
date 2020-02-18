from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets

from results.models.sports import Sport
from results.serializers.sports import SportSerializer


class SportViewSet(viewsets.ModelViewSet):
    """API endpoint for sports.

    list:
    Returns a list of all the existing sports.

    retrieve:
    Returns the given sport.

    create:
    Creates a new sport instance.

    update:
    Updates a given sport.

    partial_update:
    Updates a given sport.

    destroy:
    Removes the given sport.
    """
    permission_classes = (DRYPermissions,)
    queryset = Sport.objects.all()
    serializer_class = SportSerializer

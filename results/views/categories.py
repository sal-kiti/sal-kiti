from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import viewsets

from results.models.categories import Category, Division
from results.serializers.categories import CategorySerializer, DivisionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for categories.

    list:
    Returns a list of all the existing categories.

    retrieve:
    Returns the given category.

    create:
    Creates a new category instance.

    update:
    Updates a given category.

    partial_update:
    Updates a given category.

    destroy:
    Removes the given category.
    """
    permission_classes = (DRYPermissions,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sport']


class DivisionViewSet(viewsets.ModelViewSet):
    """API endpoint for divisions.

    list:
    Returns a list of all the existing divisions.

    retrieve:
    Returns the given division.

    create:
    Creates a new division instance.

    update:
    Updates a given division.

    partial_update:
    Updates a given division.

    destroy:
    Removes the given division.
    """
    permission_classes = (DRYPermissions,)
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

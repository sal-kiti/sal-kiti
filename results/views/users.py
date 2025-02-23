from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from results.models.organizations import Organization


@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "is_authenticated": {"type": "boolean"},
                "is_superuser": {"type": "boolean"},
                "is_staff": {"type": "boolean"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "manager": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
            },
        }
    },
)
@never_cache
@api_view()
def current_user(request):
    """
    User info endpoint.
    """
    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email
        manager = list(
            Organization.objects.filter(areas__group__in=request.user.groups.all())
            .order_by("id")
            .values_list("id", flat=True)
        )
    else:
        first_name = ""
        last_name = ""
        email = ""
        manager = []

    data = {
        "is_authenticated": request.user.is_authenticated,
        "is_superuser": request.user.is_superuser,
        "is_staff": request.user.is_staff,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "manager": manager,
    }
    return JsonResponse(data)

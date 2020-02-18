from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view


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
    else:
        first_name = ""
        last_name = ""
        email = ""

    data = {
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }
    return JsonResponse(data)

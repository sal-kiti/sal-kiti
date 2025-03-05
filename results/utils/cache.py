from django.contrib.auth.models import User
from django.core.cache import cache


def get_user_groups(user_id):
    """
    Cache user groups for permission checks.

    It's recommended to use this to report permissions to frontend and
    check access from actual groups when modifying information.

    :param user_id:
    :return: user groups
    """
    cache_key = f"user_groups_{user_id}"
    cached_groups = cache.get(cache_key)
    if cached_groups is None:
        groups = User.objects.get(pk=user_id).groups.all()
        cache.set(cache_key, groups, 15)
        return groups
    return cached_groups

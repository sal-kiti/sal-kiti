from threading import local

_local = local()


def get_current_user():
    return getattr(_local, 'user', None)


class CurrentUserMiddleware(object):
    """ Middleware for getting a request user value.

    Used in writing change log.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        _local.user = request.user
        return response

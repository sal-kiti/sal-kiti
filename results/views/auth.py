from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


class LocalLoginView(LoginView):
    """
    LoginView with the custom login form.
    """

    template_name = "registration/login.html"


@method_decorator([csrf_protect, never_cache], name="post")
class LocalLogoutView(LogoutView):
    """
    Custom logout view.
    """

    http_method_names = ["get", "head", "post", "options"]
    template_name = "registration/logout.html"

    def get(self, request, *args, **kwargs):
        """
        Redirect get to post. Support to get logouts was removed in Django 5.0.
        """
        return super().post(request, *args, **kwargs)

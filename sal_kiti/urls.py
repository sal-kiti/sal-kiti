from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from results.routers import router
from results.views.auth import LocalLoginView, LocalLogoutView
from results.views.statistics import statistics_pohjolan_malja
from results.views.users import current_user

admin.site.site_title = _("Kiti admin")
admin.site.site_header = _("Kiti administration")
admin.site.index_title = _("Kiti administration")

urlpatterns = [
    path("api/sal/pohjolanmalja/<int:year>/", statistics_pohjolan_malja, name="sal-pohjolan-malja"),
    path("api/users/current/", current_user, name="current-user"),
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
    path("auth/login/", LocalLoginView.as_view(), name="login"),
    path("auth/logout/", LocalLogoutView.as_view(), name="logout"),
    path("auth/", include("django.contrib.auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("swagger/", RedirectView.as_view(url="/api/schema/swagger/")),
    path("", TemplateView.as_view(template_name="index.html")),
]

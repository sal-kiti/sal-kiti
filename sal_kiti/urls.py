from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from rest_framework.documentation import include_docs_urls
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from results.routers import router
from results.views.statistics import statistics_pohjolan_malja
from results.views.users import current_user


schema_view = get_schema_view(
   openapi.Info(
      title=settings.API_TITLE,
      default_version=settings.API_VERSION,
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

admin.site.site_title = _('Kiti admin')
admin.site.site_header = _('Kiti administration')
admin.site.index_title = _('Kiti administration')

urlpatterns = [
    path('api/sal/pohjolanmalja/<int:year>/', statistics_pohjolan_malja, name='sal-pohjolan-malja'),
    path('api/users/current/', current_user, name='current-user'),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('docs/', include_docs_urls(title="SAL Kiti", description="SAL Kiti")),
    re_path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', TemplateView.as_view(template_name='index.html')),
]

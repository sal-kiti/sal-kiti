from django.contrib import admin

from results.models.athletes import Athlete, AthleteInformation
from results.models.categories import Category, CategoryForCompetitionType, Division
from results.models.competitions import Competition, CompetitionLevel, CompetitionResultType, CompetitionType
from results.models.competitions import CompetitionLayout
from results.models.events import Event
from results.models.organizations import Area, Organization
from results.models.records import Record, RecordLevel
from results.models.results import Result, ResultPartial
from results.models.sports import Sport
from results.models.statistics import StatisticsLink


class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']
    search_fields = ['name', 'abbreviation']


admin.site.register(Area, AreaAdmin)


class AthleteAdmin(admin.ModelAdmin):
    list_display = ['sport_id', 'first_name', 'last_name', 'organization']
    search_fields = ['sport_id', 'first_name', 'last_name']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('organization')
        return queryset


admin.site.register(Athlete, AthleteAdmin)


class AthleteInformationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['athlete']
    list_display = ['athlete', 'type', 'value', 'date_start', 'date_end', 'visibility']
    search_fields = ['athlete']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('athlete', 'athlete__organization')
        return queryset


admin.site.register(AthleteInformation, AthleteInformationAdmin)


class CategoryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['sport']
    list_display = ['sport', 'name', 'abbreviation', 'gender', 'min_age', 'max_age', 'team']
    search_fields = ['name', 'abbreviation']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('sport')
        return queryset


admin.site.register(Category, CategoryAdmin)


class CategoryForCompetitionTypeAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category', 'type']
    list_display = ['category', 'type', 'max_result', 'min_result']
    search_fields = ['category', 'type']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('category__sport', 'type__sport')
        return queryset


admin.site.register(CategoryForCompetitionType, CategoryForCompetitionTypeAdmin)


class CompetitionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['organization', 'event', 'type', 'level']
    search_fields = ['name', 'date_start']


admin.site.register(Competition, CompetitionAdmin)


class CompetitionLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']
    search_fields = ['name', 'abbreviation']


admin.site.register(CompetitionLevel, CompetitionLevelAdmin)


class CompetitionResultTypeAdmin(admin.ModelAdmin):
    autocomplete_fields = ['competition_type']
    list_display = ['competition_type', 'name', 'abbreviation', 'max_result', 'min_result', 'records']
    search_fields = ['competition_type__name', 'competition_type__abbreviation', 'name', 'abbreviation']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('competition_type__sport')
        return queryset


admin.site.register(CompetitionResultType, CompetitionResultTypeAdmin)


class CompetitionTypeAdmin(admin.ModelAdmin):
    list_display = ['sport', 'name', 'abbreviation']
    search_fields = ['name', 'abbreviation']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('sport')
        return queryset


admin.site.register(CompetitionType, CompetitionTypeAdmin)


class CompetitionLayoutAdmin(admin.ModelAdmin):
    list_display = ['type', 'label', 'name', 'block', 'row', 'col']
    search_fields = ['type', 'label', 'name']


admin.site.register(CompetitionLayout, CompetitionLayoutAdmin)


class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']
    search_fields = ['name', 'abbreviation']


admin.site.register(Division, DivisionAdmin)


class EventAdmin(admin.ModelAdmin):
    autocomplete_fields = ['organization']
    search_fields = ['name', 'date_start']


admin.site.register(Event, EventAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['name', 'abbreviation']


admin.site.register(Organization, OrganizationAdmin)


class RecordAdmin(admin.ModelAdmin):
    autocomplete_fields = ['result', 'partial_result', 'level', 'type', 'category']
    list_display = ['result', 'partial_result', 'level', 'type', 'category', 'date_start', 'date_end']
    search_fields = ['result__competition__name']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('result__competition', 'partial_result__result',
                                             'partial_result__result__competition',
                                             'partial_result__type__competition_type',
                                             'partial_result__type__competition_type__sport',
                                             'type__sport', 'category__sport')
        return queryset


admin.site.register(Record, RecordAdmin)


class RecordLevelAdmin(admin.ModelAdmin):
    autocomplete_fields = ['levels', 'types']
    list_display = ['name', 'abbreviation']
    search_fields = ['name', 'abbreviation']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('types__sport')
        return queryset


admin.site.register(RecordLevel, RecordLevelAdmin)


class ResultAdmin(admin.ModelAdmin):
    autocomplete_fields = ['athlete', 'competition', 'organization', 'category', 'elimination_category', 'team_members']
    search_fields = ['athlete__sport_id', 'athlete__first_name', 'athlete__last_name', 'competition__name']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('competition')
        return queryset


admin.site.register(Result, ResultAdmin)


class ResultPartialAdmin(admin.ModelAdmin):
    autocomplete_fields = ['result', 'type']
    list_display = ['result', 'type', 'order', 'value']
    search_fields = ['result__athlete__sport_id', 'result__athlete__first_name', 'result__athlete__last_name',
                     'result__competition__name', 'result__id']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('type__competition_type__sport')
        return queryset


admin.site.register(ResultPartial, ResultPartialAdmin)


class SportAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'order']
    search_fields = ['name', 'abbreviation']


admin.site.register(Sport, SportAdmin)


class StatisticsLinkAdmin(admin.ModelAdmin):
    list_display = ['group', 'name', 'link', 'order', 'public']
    search_fields = ['group', 'name']


admin.site.register(StatisticsLink, StatisticsLinkAdmin)

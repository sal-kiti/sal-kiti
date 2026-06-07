from django.contrib import admin

from divari.models import Competition, Result, Season, Team


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ["organization", "date"]
    search_fields = ["organization", "date"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related("organization")
        return queryset


admin.site.register(Competition, CompetitionAdmin)


class SeasonAdmin(admin.ModelAdmin):
    list_display = ["name", "date_start", "date_end", "result_count"]
    search_fields = ["name", "date_start", "date_end"]


admin.site.register(Season, SeasonAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ["season", "organization", "bow_type", "number", "division"]
    search_fields = ["organization", "bow_type", "season"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related("organization")
        return queryset


admin.site.register(Team, TeamAdmin)


class ResultAdmin(admin.ModelAdmin):
    list_display = ["competition", "bow_type", "target_type", "athlete", "result"]
    search_fields = ["competition", "bow_type", "athlete"]


admin.site.register(Result, ResultAdmin)

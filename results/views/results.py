import re

from datetime import datetime

from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import exceptions, filters, mixins, viewsets

from results.models.results import Result, ResultPartial
from results.serializers.results import ResultSerializer, ResultPartialSerializer, ResultLimitedSerializer
from results.serializers.results import ResultLimitedAggregateSerializer
from results.serializers.results_detail import ResultDetailSerializer
from results.utils.pagination import CustomPagePagination


class ResultViewSet(viewsets.ModelViewSet):
    """API endpoint for results.

    list:
    Returns a list of all the existing results.

    retrieve:
    Returns the given result.

    create:
    Creates a new result instance.

    update:
    Updates a given result.

    partial_update:
    Updates a given result.

    destroy:
    Removes the given result.
    """
    permission_classes = (DRYPermissions,)
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['competition']

    def get_queryset(self):
        """
        Prefetch partial results
        """
        self.queryset = self.queryset.prefetch_related('partial')

        return self.queryset


class ResultPartialViewSet(viewsets.ModelViewSet):
    """ API endpoint for partial results.

    list:
    Returns a list of all the existing partial results.

    retrieve:
    Returns the given partial result.

    create:
    Creates a new partial result instance.

    update:
    Updates a given partial result.

    partial_update:
    Updates a given partial result.

    destroy:
    Removes the given partial result.
    """
    permission_classes = (DRYPermissions,)
    queryset = ResultPartial.objects.all()
    serializer_class = ResultPartialSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('athlete',
                          openapi.IN_QUERY,
                          description='Multiple values may be separated by commas.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('category',
                          openapi.IN_QUERY,
                          description='Multiple values may be separated by commas.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('competition',
                          openapi.IN_QUERY,
                          description='Multiple values may be separated by commas.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('level',
                          openapi.IN_QUERY,
                          description='Multiple values may be separated by commas.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('organization',
                          openapi.IN_QUERY,
                          description='Multiple values may be separated by commas.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('type',
                          openapi.IN_QUERY,
                          description='Multiple values may be separated by commas.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('sport',
                          openapi.IN_QUERY,
                          description='Multiple values may be separated by commas.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('start_date',
                          openapi.IN_QUERY,
                          description='Date in %Y-%m-%d (i.e. 2019-01-01) format.',
                          type=openapi.TYPE_STRING),
        openapi.Parameter('end_date',
                          openapi.IN_QUERY,
                          description='Date in %Y-%m-%d (i.e. 2019-01-01) format.',
                          type=openapi.TYPE_STRING),
        openapi.Parameter('approved',
                          openapi.IN_QUERY,
                          description='Limit to approved results.',
                          type=openapi.TYPE_BOOLEAN),
        openapi.Parameter('trial',
                          openapi.IN_QUERY,
                          description='Limit to trial competitions.',
                          type=openapi.TYPE_BOOLEAN),
        openapi.Parameter('external',
                          openapi.IN_QUERY,
                          description='Include external athletes.',
                          type=openapi.TYPE_BOOLEAN),
        openapi.Parameter('group_results',
                          openapi.IN_QUERY,
                          description='Sum of x best results by athlete.',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('fields',
                          openapi.IN_QUERY,
                          description='Include only fields in results. Use != for excluding fields.',
                          type=openapi.TYPE_STRING),
    ]
))
class ResultList(mixins.ListModelMixin, viewsets.GenericViewSet):
    """API endpoint for retrieving result lists.

    group_results returns limited information, including only athlete and result.

    retrieve:
    Returns the result list
    """
    pagination_class = CustomPagePagination
    permission_classes = (DRYPermissions,)
    queryset = Result.objects.all()
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('competition__start_date', 'category', 'position', 'result')
    ordering = ('-result')
    serializer_class = ResultLimitedSerializer

    @staticmethod
    def _build_raw_query(queryset):
        """
        Build a raw query for grouping results with inner query.
        """
        raw_query = str(queryset.query)
        if 'WHERE' in raw_query:
            where_query = ' WHERE' + raw_query.split('WHERE')[1].split(' ORDER BY')[0]
            for match in re.findall(r' \d{4}-\d{2}-\d{2}', raw_query):
                where_query = where_query.replace(match, ' "' + match.strip() + '"')
            joins = re.split('FROM .results_result.', raw_query)[1].split('WHERE')[0]
        else:
            where_query = ''
            joins = re.split('FROM .results_result.', raw_query)[1].split('ORDER BY')[0]
        select_query = raw_query.split('FROM')[0]
        first_select = re.sub('.results_result...result.,', 'SUM(`results_result`.`result`) `result`,', select_query)
        second_select = select_query + (', ROW_NUMBER() OVER(PARTITION BY `results_result`.`athlete_id` '
                                        'ORDER BY `results_result`.`result` DESC) `rn` ')
        query_end = (') `results_result` WHERE `rn` <= %s GROUP BY `results_result`.`athlete_id` '
                     'ORDER BY SUM(`result`) DESC')
        raw_query = first_select + 'FROM (' + second_select + 'FROM `results_result`' + joins + where_query + query_end
        return raw_query

    def get_queryset(self):
        """
        Custom filtering with query parameters.
        """
        queryset = Result.objects.all()
        try:
            competition = self.request.query_params.get('competition', None)
            if competition and int(competition) >= 0:
                queryset = queryset.filter(competition=competition)
                self.pagination_class = None

            athlete = self.request.query_params.get('athlete', None)
            if athlete and int(athlete) >= 0:
                queryset = queryset.filter(athlete__pk=athlete)
                self.pagination_class = None

            sport = self.request.query_params.get('sport', None)
            if sport:
                sport_list = [int(c) for c in sport.split(",")]
                queryset = queryset.filter(competition__type__sport__pk__in=sport_list)

            category = self.request.query_params.get('category', None)
            if category:
                category_list = [int(c) for c in category.split(",")]
                queryset = queryset.filter(category__pk__in=category_list)

            competition_level = self.request.query_params.get('level', None)
            if competition_level:
                competition_level_list = [int(c) for c in competition_level.split(",")]
                queryset = queryset.filter(competition__level__pk__in=competition_level_list)

            competition_type = self.request.query_params.get('type', None)
            if competition_type:
                competition_type_list = [int(c) for c in competition_type.split(",")]
                queryset = queryset.filter(competition__type__pk__in=competition_type_list)

            organization = self.request.query_params.get('organization', None)
            if organization:
                organization_list = [int(c) for c in organization.split(",")]
                queryset = queryset.filter(organization__in=organization_list)

            start_date = self.request.query_params.get('start', None)
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(competition__date_end__gte=start_date)

            end_date = self.request.query_params.get('end', None)
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(competition__date_start__lte=end_date)

            approved = self.request.query_params.get('approved', False)
            if approved:
                queryset = queryset.filter(approved=True)

            trial = self.request.query_params.get('trial', False)
            if trial:
                queryset = queryset.filter(competition__trial=True)

            external = self.request.query_params.get('external', False)
            if not external:
                queryset = queryset.exclude(organization__external=True)

        except ValueError:
            raise exceptions.ParseError()

        group_results = self.request.query_params.get('group_results', None)
        if group_results and group_results.isdigit() and int(group_results) > 1:
            self.serializer_class = ResultLimitedAggregateSerializer
            self.ordering = None
            self.ordering_fields = None
            self.filter_backends = []
            queryset = Result.objects.raw(self._build_raw_query(queryset), [int(group_results)])
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class ResultDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """API endpoint for retrieving detailed result information.

    retrieve:
    Returns the detailed information, including partial results, for a single result.
    """
    permission_classes = (DRYPermissions,)
    queryset = Result.objects.all()
    serializer_class = ResultDetailSerializer

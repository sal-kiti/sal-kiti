class EagerLoadingMixin:
    """
    Mixin to select_related and prefetch_related queries
    From the comments of http://ses4j.github.io/2015/11/23/optimizing-slow-django-rest-framework-performance/
    """

    @classmethod
    def setup_eager_loading(cls, queryset, prefetch=None):
        """
        Sets select_related and prefetch_related attributes to queryset if specified in serializer

        :param queryset:
        :param prefetch: list of Prefetch objects not included in _PREFETCH_RELATED_FIELDS
        :return: queryset including select_related and prefetch_related attributes
        :rtype: QuerySet
        """
        if hasattr(cls, "_SELECT_RELATED_FIELDS"):
            queryset = queryset.select_related(*cls._SELECT_RELATED_FIELDS)
        if hasattr(cls, "_PREFETCH_RELATED_FIELDS"):
            if prefetch:
                queryset = queryset.prefetch_related(*prefetch, *cls._PREFETCH_RELATED_FIELDS)
            else:
                queryset = queryset.prefetch_related(*cls._PREFETCH_RELATED_FIELDS)
        return queryset

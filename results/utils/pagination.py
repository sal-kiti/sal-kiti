from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class CustomPagePagination(pagination.PageNumberPagination):
    """
    Custom pagination class to use with Vue Bootstrap pagination.
    """

    page_size_query_param = "limit"

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("count", self.page.paginator.count),
                    ("page", self.page.number),
                    ("limit", self.get_page_size(self.request)),
                    ("num_page", self.page.paginator.num_pages),
                    ("results", data),
                ]
            )
        )

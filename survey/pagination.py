from rest_framework import pagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'offset': self.offset,
            'results': data,
        })


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

class FHIRBundlePagination(PageNumberPagination):
    page_size = 50  # Default number of patients per page
    page_size_query_param = '_count' # FHIR uses _count for page size
    max_page_size = 500

    def get_paginated_response(self, data):
        """
        Formats the paginated response to comply with FHIR Bundle searchset.
        """
        links = []
        
        # Self link
        links.append({
            "relation": "self",
            "url": self.request.build_absolute_uri()
        })
        
        # Next link
        if self.get_next_link():
            links.append({
                "relation": "next",
                "url": self.get_next_link()
            })
            
        # Previous link
        if self.get_previous_link():
            links.append({
                "relation": "previous",
                "url": self.get_previous_link()
            })

        return Response(OrderedDict([
            ('resourceType', 'Bundle'),
            ('type', 'searchset'),
            ('total', self.page.paginator.count),
            ('link', links),
            ('entry', [{'resource': item} for item in data])
        ]))
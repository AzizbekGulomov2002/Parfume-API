from rest_framework.pagination import PageNumberPagination

class BasePagination(PageNumberPagination):
    page_size = 10  # Define your pagination settings

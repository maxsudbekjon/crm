from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20                # avtomatik 20 ta item
    page_size_query_param = None  # foydalanuvchi o'zgartira olmaydi
    max_page_size = 20

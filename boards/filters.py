from django_filters import rest_framework as filters
from .models import Board

class BoardFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    # description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    
    class Meta:
        model = Board
        fields = ['title']
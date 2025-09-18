from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.db.models import Avg

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def average_price(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'detail':'category_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cat = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({'detail':'category not found'}, status=status.HTTP_404_NOT_FOUND)
        descendants = cat.get_descendants()
        category_ids = [cat.id] + [d.id for d in descendants]
        avg = Product.objects.filter(category_id__in=category_ids).aggregate(Avg('price'))['price__avg']
        return Response({'category': cat.name, 'average_price': avg})
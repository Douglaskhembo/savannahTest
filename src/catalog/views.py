from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsAdminOrReadOnly
from django.db.models import Avg, ProtectedError
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete category because it still has products."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=['get'])
    def average_price(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {"detail": "Parameter 'category_id' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response(
                {"detail": f"Category with id {category_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            descendants = category.get_descendants()
            category_ids = [category.id] + list(descendants.values_list("id", flat=True))
            avg_price = Product.objects.filter(category_id__in=category_ids).aggregate(
                avg=Avg("price")
            )["avg"] or 0
        except Exception as e:
            return Response(
                {"detail": f"Error calculating average price: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "category": category.name,
            "average_price": avg_price
        })

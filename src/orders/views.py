from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from .permissions import IsOwnerOrAdmin


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = Order.objects.filter(is_deleted=False)
        if self.request.user.role != "ADMIN":
            qs = qs.filter(customer=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.role == "ADMIN":
            instance.delete(hard=True)
        else:
            instance.delete()

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from src.catalog.views import CategoryViewSet, ProductViewSet
from src.orders.views import OrderViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]
from rest_framework import serializers
from .models import Order, OrderProducts
from src.catalog.serializers import ProductSerializer
from src.catalog.models import Product
from src.core.notifications import notify_order_placed

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderProducts
        fields = ('id','product_id','quantity','price')
        read_only_fields = ('price',)

    def create(self, validated_data):
        product = Product.objects.get(pk=validated_data['product_id'])
        validated_data['price'] = product.price
        validated_data['product'] = product
        validated_data.pop('product_id', None)
        return OrderProducts.objects.create(**validated_data)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'order_code', 'customer', 'created_at', 'total', 'status', 'items')
        read_only_fields = ('id', 'created_at', 'total', 'status', 'order_code', 'customer')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0
        for item in items_data:
            item['order'] = order
            oi = OrderItemSerializer().create(item)
            total += oi.price * oi.quantity
        order.total = total
        order.save()

        # trigger notifications
        notify_order_placed(order)
        return order

from rest_framework import serializers
from .models import Category, Product

class hierarchicalField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.ListSerializer(child=hierarchicalField(), read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children']

class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ['id', 'product_code', 'name', 'price', 'category']
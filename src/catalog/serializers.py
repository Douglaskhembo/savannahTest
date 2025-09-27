from rest_framework import serializers
from .models import Category, Product


class HierarchicalField(serializers.Serializer):
    def to_representation(self, value):
        serializer_class = self.parent.parent.__class__
        depth = self.context.get("depth", 0)

        if depth >= 3:
            return {"id": value.id, "name": value.name}

        serializer = serializer_class(
            value,
            context={**self.context, "depth": depth + 1}
        )
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = HierarchicalField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'category_code', 'name', 'parent', 'children']
        read_only_fields = ['id', 'category_code', 'children', 'parent']

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
        default=None
    )

    def validate(self, attrs):
        if self.instance and attrs.get("parent") == self.instance:
            raise serializers.ValidationError(
                "A category cannot be its own parent."
            )
        return attrs

    def update(self, instance, validated_data):
        if "parent" not in validated_data:
            validated_data["parent"] = instance.parent
        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ['id', 'product_code', 'name', 'price', 'category']
        read_only_fields = ['id', 'product_code']

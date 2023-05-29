from rest_framework.serializers import ModelSerializer
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import Product, Tag, ProductOption


class ProductOptionSerializer(ModelSerializer):
    class Meta:
        model = ProductOption
        fields = (
            "pk",
            "name",
            "price",
        )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "pk",
            "name",
        )


class ProductSerializer(WritableNestedModelSerializer):
    option_set = ProductOptionSerializer(many=True, read_only=True)
    tag_set = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "option_set",
            "tag_set",
        )

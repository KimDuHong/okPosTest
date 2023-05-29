from rest_framework.viewsets import ModelViewSet
from .models import Product
from .serializers import ProductSerializer
from drf_yasg.utils import swagger_auto_schema


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("tag_set", "option_set")
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # @swagger_auto_schema(
    #     request_body=ProductSerializer,
    #     responses={
    #         200: ProductSerializer,
    #     },
    # )
    # def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)


# class ProductDetail(ModelViewSet):

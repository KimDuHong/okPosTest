from django.db import transaction
from django.db import IntegrityError
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from .serializers import ProductSerializer, TagSerializer, ProductOptionSerializer
from .models import Product, Tag, ProductOption


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("tag_set", "option_set")
    serializer_class = ProductSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        option_data = data.pop("option_set", [])
        tag_data = data.pop("tag_set", [])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        product = serializer.instance

        # Create ProductOptions
        for option in option_data:
            ProductOption.objects.create(product=product, **option)

        try:
            for tag in tag_data:
                if "name" not in tag:
                    raise ValidationError("태그명은 필수 입력 값입니다.")

                if "pk" in tag:
                    tag_obj = Tag.objects.get(pk=tag["pk"], name=tag["name"])
                else:
                    tag_obj = Tag.objects.create(name=tag["name"])
                product.tag_set.add(tag_obj)

        except Tag.DoesNotExist:
            raise NotFound

        except IntegrityError:
            already_tag = tag.get("name", None)
            if already_tag:
                raise ValidationError(f"해당 태그명 ({already_tag}) 은/는  이미 존재합니다.")
            else:
                raise ValidationError("태그명은 필수 입력 값입니다.")

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

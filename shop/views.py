from django.db import transaction, IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
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

        product_options = []
        for option in option_data:
            if "name" in option and "price" in option:
                try:
                    price = int(option["price"])
                except ValueError:
                    raise ValidationError("가격은 숫자로 입력해야 합니다.")

                product_options.append(ProductOption(product=product, **option))
            else:
                raise ValidationError("옵션명과 가격은 필수 입력 값입니다.")

        ProductOption.objects.bulk_create(product_options)

        new_tags = []
        exist_tags = []
        for tag in tag_data:
            if "name" in tag and "pk" not in tag:
                new_tags.append(Tag(name=tag["name"]))
            elif "name" in tag and "pk" in tag:
                exist_tags.append(tag)
            elif "name" not in tag:
                raise ValidationError("태그명은 필수 입력 값입니다.")

        if new_tags:
            try:
                Tag.objects.bulk_create(new_tags)
            except IntegrityError:
                raise ValidationError("태그명은 중복될 수 없습니다.")

        all_tags = Tag.objects.filter(
            Q(name__in=[tag.name for tag in new_tags])
            | Q(
                pk__in=[tag["pk"] for tag in exist_tags],
                name__in=[tag["name"] for tag in exist_tags],
            )
        )

        product.tag_set.set(all_tags)

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        data = request.data

        option_data = data.pop("option_set", [])
        tag_data = data.pop("tag_set", [])

        existing_option_pks = [
            option.get("pk") for option in option_data if option.get("pk")
        ]
        ProductOption.objects.filter(
            product=product,
        ).exclude(
            pk__in=existing_option_pks,
        ).delete()

        new_option_objects = []
        exist_option_objects = []
        for option in option_data:
            if "name" not in option:
                raise ValidationError("옵션명은 필수 입력 값입니다.")

            if "price" not in option:
                raise ValidationError("가격은 필수 입력 값입니다.")
            else:
                try:
                    price = int(option["price"])
                except ValueError:
                    raise ValidationError("가격은 숫자로 입력해야 합니다.")

            if "pk" in option:
                exist_option_objects.append(
                    ProductOption(
                        pk=option["pk"],
                        product=product,
                        name=option["name"],
                        price=option["price"],
                    )
                )
            else:
                new_option_objects.append(
                    ProductOption(
                        product=product, name=option["name"], price=option["price"]
                    )
                )

        ProductOption.objects.bulk_update(
            exist_option_objects,
            fields=["name", "price"],
        )
        ProductOption.objects.bulk_create(new_option_objects)

        new_tags = []
        exist_tags = []
        for tag in tag_data:
            if "name" in tag and "pk" not in tag:
                new_tags.append(Tag(name=tag["name"]))
            elif "name" in tag and "pk" in tag:
                exist_tags.append(tag)
            elif "name" not in tag:
                raise ValidationError("태그명은 필수 입력 값입니다.")

        if new_tags:
            try:
                Tag.objects.bulk_create(new_tags, ignore_conflicts=True)
            except IntegrityError:
                raise ValidationError("태그명은 중복될 수 없습니다.")

        all_tags = Tag.objects.filter(
            Q(name__in=[tag.name for tag in new_tags])
            | Q(
                pk__in=[tag["pk"] for tag in exist_tags],
                name__in=[tag["name"] for tag in exist_tags],
            )
            | Q(product=product)
        )
        product.tag_set.set(all_tags)

        return Response(ProductSerializer(product).data)

from django.db import transaction, IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, ParseError
from .serializers import ProductSerializer
from .models import Product, Tag, ProductOption


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("tag_set", "option_set")
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "option_set", "tag_set"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="상품명",
                ),
                "option_set": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="옵션 추가",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "name": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="옵션 이름 (required)",
                            ),
                            "price": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="옵션 가격 (required)",
                            ),
                        },
                    ),
                ),
                "tag_set": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="태그 리스트",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "pk": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="기존에 존재하는 태그 연결시 사용, Null 시 새로운 태그 생성",
                            ),
                            "name": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="태그 명 (required), 고유한 값",
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={
            201: openapi.Response(description="Created", schema=ProductSerializer),
            400: "Bad Request",
        },
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data

        if "option_set" not in data or "tag_set" not in data:
            raise ParseError("잘못된 데이터입니다.")

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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["pk", "name", "option_set", "tag_set"],
            properties={
                "pk": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="변경하려는 상품의 pk",
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="상품명",
                ),
                "option_set": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="옵션 추가 / 변경 / 삭제",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "pk": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="기존에 존재하는 옵션 연결 및 수정시에 사용, Null 시 새로운 옵션 생성",
                            ),
                            "name": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="옵션 이름 (required)",
                            ),
                            "price": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="옵션 가격 (required)",
                            ),
                        },
                    ),
                ),
                "tag_set": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="태그 리스트",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "pk": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="기존에 존재하는 태그 연결시 사용, Null 시 새로운 태그 생성",
                            ),
                            "name": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="태그 명 (required), 고유한 값",
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={
            201: openapi.Response(description="Created", schema=ProductSerializer),
            400: "Bad Request",
        },
    )
    @transaction.atomic
    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        if (
            "option_set" not in data
            or "tag_set" not in data
            or "name" not in data
            or "pk" not in data
        ):
            raise ParseError("잘못된 데이터입니다.")

        if data.get("pk") != pk:
            raise ParseError("잘못된 접근입니다.")

        product = get_object_or_404(Product, pk=pk)

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
                Tag.objects.bulk_create(new_tags)
                # Tag.objects.bulk_create(new_tags, ignore_conflicts=True)
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

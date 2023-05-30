import pytest
from collections import OrderedDict
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Product, ProductOption, Tag


# Shop/product GET TEST
@pytest.mark.django_db
class TestProductGetAPI:
    def setup_method(cls):
        cls.client = APIClient()
        cls.url = reverse("product-list")
        product = Product.objects.create(name="TestProduct")
        Product.objects.create(name="TestProduct2")
        for i in range(3):
            ProductOption.objects.create(
                product=product,
                name=f"TestOption{i+1}",
                price=(2 - i) * 500,
            )
        tags = [Tag.objects.create(name="ExistTag"), Tag.objects.create(name="NewTag")]
        product.tag_set.set(tags)

    def test_view_product_list_success(self):
        request_data = [
            OrderedDict(
                [
                    ("pk", 1),
                    ("name", "TestProduct"),
                    (
                        "option_set",
                        [
                            OrderedDict(
                                [("pk", 1), ("name", "TestOption1"), ("price", 1000)]
                            ),
                            OrderedDict(
                                [("pk", 2), ("name", "TestOption2"), ("price", 500)]
                            ),
                            OrderedDict(
                                [("pk", 3), ("name", "TestOption3"), ("price", 0)]
                            ),
                        ],
                    ),
                    (
                        "tag_set",
                        [
                            OrderedDict([("pk", 1), ("name", "ExistTag")]),
                            OrderedDict([("pk", 2), ("name", "NewTag")]),
                        ],
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("pk", 2),
                    ("name", "TestProduct2"),
                    ("option_set", []),
                    ("tag_set", []),
                ]
            ),
        ]

        response = self.client.get(self.url, format="json")
        assert response.status_code == 200
        assert response.data == request_data


# Shop/product POST TEST
@pytest.mark.django_db
class TestProductPostAPI:
    def setup_method(cls):
        cls.client = APIClient()
        cls.url = reverse("product-list")
        Tag.objects.create(name="ExistTag")

    def test_create_product_success(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "NewTag"}],
        }
        response_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "TestOption2", "price": 500},
                {"pk": 3, "name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"pk": 2, "name": "NewTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 201
        assert Product.objects.count() == 1
        assert response.data == response_data
        product = Product.objects.first()

        assert product.name == "TestProduct"
        assert product.option_set.count() == 3

        options = product.option_set.all()
        for i, option in enumerate(options):
            assert option.name == f"TestOption{i+1}"
            assert option.price == (2 - i) * 500

    def test_create_product_fail_non_name(self):
        request_data = {
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "NewTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_fail_non_option(self):
        request_data = {
            "name": "TestProduct",
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "NewTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_success_option_null(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "NewTag"}],
        }
        response_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"pk": 2, "name": "NewTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 201
        assert response.data == response_data

    def test_create_product_fail_option_name_null(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "NewTag"}],
        }
        response_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"pk": 2, "name": "NewTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_fail_option_price_null(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1"},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "NewTag"}],
        }
        response_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"pk": 2, "name": "NewTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_fail_non_tag(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
        }
        response_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "TestOption2", "price": 500},
                {"pk": 3, "name": "TestOption3", "price": 0},
            ],
            "tag_set": [],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_success_tag_null(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [],
        }
        response_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "TestOption2", "price": 500},
                {"pk": 3, "name": "TestOption3", "price": 0},
            ],
            "tag_set": [],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 201
        assert response.data == response_data

    def test_create_product_fail_option_price_is_string(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": "Error"},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "NewTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_fail_tag_name_is_duplicate(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "ExistTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_fail_tag_name_null_pk_exist(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1}, {"name": "ExistTag"}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_fail_tag_name_null_pk_not_exist(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": 0},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {}],
        }
        response = self.client.post(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_create_product_fail_test_transcation(self):
        request_data = {
            "name": "TestProduct",
            "option_set": [
                {"name": "TestOption1", "price": 1000},
                {"name": "TestOption2", "price": 500},
                {"name": "TestOption3", "price": "Error"},
            ],
            "tag_set": [{"pk": 1, "name": "ExistTag"}, {"name": "ExistTag"}],
        }
        self.client.post(self.url, request_data, format="json")
        assert Product.objects.count() == 0


# Shop/product/<int:pk> GET TEST
@pytest.mark.django_db
class TestProductDetailGetAPI:
    def setup_method(cls):
        cls.client = APIClient()
        cls.url = reverse("product-detail", kwargs={"pk": 1})
        product = Product.objects.create(name="TestProduct")
        for i in range(3):
            ProductOption.objects.create(
                product=product,
                name=f"TestOption{i+1}",
                price=(2 - i) * 500,
            )
        tags = [Tag.objects.create(name="ExistTag"), Tag.objects.create(name="NewTag")]
        product.tag_set.set(tags)

    def test_view_product_retrieve_success(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                OrderedDict([("pk", 1), ("name", "TestOption1"), ("price", 1000)]),
                OrderedDict([("pk", 2), ("name", "TestOption2"), ("price", 500)]),
                OrderedDict([("pk", 3), ("name", "TestOption3"), ("price", 0)]),
            ],
            "tag_set": [
                OrderedDict([("pk", 1), ("name", "ExistTag")]),
                OrderedDict([("pk", 2), ("name", "NewTag")]),
            ],
        }

        response = self.client.get(self.url, format="json")
        assert response.status_code == 200
        assert response.data == request_data


# Shop/product/<int:pk> PATCH TEST
@pytest.mark.django_db
class TestProductDetailPatchAPI:
    def setup_method(cls):
        cls.client = APIClient()
        cls.url = reverse("product-detail", kwargs={"pk": 1})
        product = Product.objects.create(name="TestProduct")
        for i in range(3):
            ProductOption.objects.create(
                product=product,
                name=f"TestOption{i+1}",
                price=(2 - i) * 500,
            )
        tags = [Tag.objects.create(name="ExistTag"), Tag.objects.create(name="NewTag")]
        product.tag_set.set(tags)
        cls.success_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }

    def test_update_product_success(self):
        request_data = self.success_data
        response_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"pk": 4, "name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"pk": 3, "name": "Edit New Tag"},
            ],
        }

        product = Product.objects.first()
        assert product.name == "TestProduct"

        # Before Patch
        assert product.option_set.count() == 3
        for option in product.option_set.all():
            assert option.pk <= 3
            if option.pk == 2:
                assert option.name == "TestOption2"
                assert option.price == 500
        assert product.tag_set.count() == 2

        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 200
        assert response.data == response_data

        # After Patch
        assert product.option_set.count() == 3
        for option in product.option_set.all():
            assert option.pk != 3
            if option.pk == 2:
                assert option.name == "Edit TestOption2"
                assert option.price == 1500
        assert product.tag_set.count() == 3

    def test_update_product_fail_wrong_access_URL(self):
        request_data = self.success_data
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": 2}), request_data, format="json"
        )
        assert response.status_code == 400

    def test_update_product_fail_non_pk(self):
        request_data = {
            "name": "TestProduct2",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }
        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_update_product_fail_non_name(self):
        request_data = {
            "pk": 1,
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }
        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_update_product_fail_non_option_set(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }
        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_update_product_success_option_null(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }

        assert ProductOption.objects.count() == 3
        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 200
        assert ProductOption.objects.count() == 0

    def test_update_product_fail_option_name_null(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }

        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_update_product_fail_option_price_null(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1"},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }

        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_update_product_fail_option_price_is_string(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": "Error"},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "Edit New Tag"},
            ],
        }

        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_update_product_fail_non_tag(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
        }

        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

    def test_update_product_success_tag_null(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [],
        }

        # Tag 는 삭제되지 않음
        assert Product.objects.first().tag_set.count() == 2
        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 200
        assert Product.objects.first().tag_set.count() == 2

    def test_update_product_fail_tag_duplicate_name(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1, "name": "ExistTag"},
                {"pk": 2, "name": "NewTag"},
                {"name": "ExistTag"},
            ],
        }
        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400
        assert Product.objects.first().tag_set.count() == 2

    def test_update_product_fail_tag_name_null(self):
        request_data = {
            "pk": 1,
            "name": "TestProduct",
            "option_set": [
                {"pk": 1, "name": "TestOption1", "price": 1000},
                {"pk": 2, "name": "Edit TestOption2", "price": 1500},
                {"name": "Edit New Option", "price": 300},
            ],
            "tag_set": [
                {"pk": 1},
                {"pk": 2, "name": "NewTag"},
            ],
        }
        response = self.client.patch(self.url, request_data, format="json")
        assert response.status_code == 400

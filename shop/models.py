# shop/models.py
from django.db import models

__all__ = (
    "Tag",
    "Product",
    "ProductOption",
)


class Tag(models.Model):
    name = models.CharField("태그명", unique=True, max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("상품명", max_length=100)
    tag_set = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.name

    # Admin 에서 확인용
    @property
    def tag_set_list(self):
        return (
            [i for i in self.tag_set.all()] if [i for i in self.tag_set.all()] else None
        )

    # Admin 에서 확인용
    @property
    def option_list(self):
        return (
            [i for i in self.option_set.all()]
            if [i for i in self.option_set.all()]
            else None
        )


class ProductOption(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="상품",
        related_name="option_set",
        related_query_name="option",
        on_delete=models.CASCADE,
    )
    name = models.CharField("옵션명", max_length=100)
    price = models.IntegerField("가격")

    def __str__(self):
        return self.name

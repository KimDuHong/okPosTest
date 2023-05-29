from django.shortcuts import render
from rest_framework.views import APIView


# Create your views here.
class ProductAll(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class ProductDetail(APIView):
    def patch(self, request, pk):
        pass

from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("buyer/<str:cnpj>", get_buyer_by_cnpj, name="get_buyer_by_cnpj"),
    path("buyer/terms/", get_terms, name="get_terms"),
    path("order/create/", order_create, name="order_create")
]

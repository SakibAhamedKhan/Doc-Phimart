from django.urls import path
from product import views

urlpatterns = [
     path('', views.ProductListing.as_view(), name="product-list"),
     path('<int:id>/', views.ProductDetails.as_view(), name="view-specific-product"),
]

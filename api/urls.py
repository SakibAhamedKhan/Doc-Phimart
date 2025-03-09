from django.urls import path, include
from product import views
from order.views import CartViewSet, CartItemViewSet, OrderViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename="products")
router.register('categories', views.CategoryViewSet)
router.register('carts', CartViewSet, basename='carts')
router.register('orders', OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='producted')
product_router.register('reviews', views.ReviewViewSet, basename='product-review')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup = 'carteddd')
cart_router.register('items', CartItemViewSet, basename='cart-item')

urlpatterns = [
     path('', include(router.urls)),
     path('', include(product_router.urls)),
     path('', include(cart_router.urls)),
     path('auth/', include('djoser.urls')),
     path('auth/', include('djoser.urls.jwt')),
     ## aro path add kora jabe
     # path('products/', include('product.product_urls')),
     # path('categories/', include('product.category_urls'))
]

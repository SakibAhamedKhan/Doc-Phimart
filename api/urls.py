from django.urls import path, include
from product import views as productViews
from order import views as orderViews
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', productViews.ProductViewSet, basename="products")
router.register('categories', productViews.CategoryViewSet)
router.register('carts', orderViews.CartViewSet, basename='carts')
router.register('orders', orderViews.OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='producted')
product_router.register('reviews', productViews.ReviewViewSet, basename='product-review')
product_router.register('images', productViews.ProductImageViewSet, basename='product-images')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup = 'carteddd')
cart_router.register('items', orderViews.CartItemViewSet, basename='cart-item')

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

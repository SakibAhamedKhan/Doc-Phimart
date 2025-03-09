from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from order.models import Cart, CartItem, Order, OrderItem
from order.serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreadteOrderSerializer, UpdateOrderSerializer, EmptySerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from order.services import OrderService
from rest_framework.response import Response

# Create your views here.
class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        if Cart.objects.filter(user=self.request.user).exists():
            raise ValidationError({"detail": "A cart already exists for this user."})
        serializer.save(user = self.request.user)
    
    def get_queryset(self):
        return Cart.objects.prefetch_related('items__product').filter(user = self.request.user)
        # return Cart.objects.all()
    
class CartItemViewSet(ModelViewSet):
    # queryset = CartItem.objects.all()
    # serializer_class = CartItemSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['carteddd_pk']}
    
    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs['carteddd_pk'])
        # return CartItem.objects.all()
    
    

class OrderViewSet(ModelViewSet):
    # queryset = Order.objects.all()
    http_method_names = ['get', 'post', 'delete', 'patch']
    # serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        OrderService.cancel_order(order=order,  user=request.user)
        return Response({'status':'Order canceled'})
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = UpdateOrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status':f'Order status updated to {request.data['status']}'})
    
    def get_permissions(self):
        if self.action in ['update_status', 'destroy', 'partial_update']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action =='cancel':
            return EmptySerializer
        elif self.action == 'create':
            return CreadteOrderSerializer
        elif self.action == 'update_status':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        return {'user_id':self.request.user.id, 'user': self.request.user}
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user = self.request.user)
    
    
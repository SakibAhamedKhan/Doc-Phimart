from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product, Category, Review
from django.shortcuts import get_object_or_404
from product.serializers import ProductSerializers, CategorySerializers, ReviewSerializer
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from product.paginations import DefaultPagination
from rest_framework.permissions import IsAdminUser, AllowAny
from api.permissions import IsAdminOrReadOnly, FullDjangoModelPermission
from rest_framework.permissions import DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly
from product.permissions import IsReviewAuthorOrReadonly

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['category_id', 'price']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'updated_date']
    permission_classes = [IsAdminOrReadOnly]
    # permission_classes = [FullDjangoModelPermission]
    
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminUser()]
    
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     category_id = self.request.query_params.get('category_id')
        
    #     if category_id is not None:
    #         queryset = Product.objects.filter(category_id=category_id)
        
    #     return queryset
    
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product.stock > 10:
            return Response({'message':"Product with stock more than 10 could not be deleted"})
        self.perform_destroy(product)
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
    

@api_view(['GET', 'POST'])
def view_products(request):
    if request.method == 'GET':
        products = Product.objects.select_related('category').all();
        serializer = ProductSerializers(products, many=True, context={'request': request}) ## Serializer ( Object to JSON )
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = ProductSerializers(data = request.data, context={'request': request}) ## Deserializer ( JSON to Object )
        # if serializer.is_valid():
        #     print(serializer.validated_data)
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
      
class ViewProducts(APIView):
    def get(self, request):
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializers(products, many=True, context={'request': request}) ## Serializer ( Object to JSON )
        return Response(serializer.data)
    def post(self, request):
        serializer = ProductSerializers(data = request.data, context={'request': request}) ## Deserializer ( JSON to Object )
        # if serializer.is_valid():
        #     print(serializer.validated_data)
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductListing(ListCreateAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializers
    
    # def get_queryset(self):
    #     return Product.objects.select_related('category').all()
    
    # def get_serializer_class(self):
    #     return ProductSerializers
    
    # def get_serializer_context(self):
    #     return {'request':self.request}
    

## ===================================================== ##
     
        
@api_view(['GET', 'PUT', 'DELETE'])
def view_specific_products(request, id):
    # try:
    #     product = Product.objects.get(pk=id)
    #     return Response({'message': product.id})
    # except Product.DoesNotExist:
    #     return Response({'message': "Product does not exists!"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        product = get_object_or_404(Product,pk=id)
        serializer = ProductSerializers(product, context={'request': request})
        return Response(serializer.data)
    if request.method == 'PUT':
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializers(product, data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    if request.method == 'DELETE':
        product = get_object_or_404(Product, pk=id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ViewSpecificProduct(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product,pk=id)
        serializer = ProductSerializers(product, context={'request': request})
        return Response(serializer.data)
    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializers(product, data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductDetails(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    lookup_field = 'id'
    
    # def delete(self, request, id):
    #     product = get_object_or_404(Product, pk=id)
    #     if product.stock > 10:
    #         return Response({'message':"Product with stock more than 10 could not be deleted"})
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT) 

## ===================================================== ##


class CategoryViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    # permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializers 

@api_view()
def view_categories(request):
    categories = Category.objects.annotate(product_count=Count('products')).all()
    serializer = CategorySerializers(categories, many=True)
    return Response(serializer.data)

class ViewCategories(APIView):
    def get(self, request):
        categories = Category.objects.annotate(product_count=Count('products')).all()
        serializer = CategorySerializers(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializers = CategorySerializers(data = request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)

class CategoryListing(ListCreateAPIView):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializers

## ===================================================== ##


@api_view()
def view_specific_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializers(category)
    return Response(serializer.data)


class ViewSpecificCategory(APIView):
    def get(self, request, pk):
        category = get_object_or_404(Category.objects.annotate(product_count=Count('products')).all(), pk=pk)
        serializer = CategorySerializers(category)
        return Response(serializer.data)
    
    def put(self, request, pk):
        category = get_object_or_404(Category.objects.annotate(product_count=Count('products')).all(), pk=pk)
        serializers = CategorySerializers(category, data = request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data)
    
    def delete(self, request, pk):
        category = get_object_or_404(Category.objects.annotate(product_count=Count('products')).all(), pk=pk)
        category.delete()
        return Response(status=status.HTTP_404_NOT_FOUND)
    
class CategoryDetails(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializers
    

## ===================================================== ##


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadonly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    # def perform_update(self, serializer):
    #     serializer.save(user=self.request.user)
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['producted_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['producted_pk']}
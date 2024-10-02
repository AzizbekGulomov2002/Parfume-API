from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductImagesViewSet, BrandViewSet, BannerViewSet, ContactViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImagesViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'banners', BannerViewSet)
router.register(r'contacts', ContactViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

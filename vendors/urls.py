from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorProfileViewSet, ServiceViewSet, ServiceVariantViewSet

router = DefaultRouter()
router.register(r'profiles', VendorProfileViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'variants', ServiceVariantViewSet)

app_name = 'vendors'

urlpatterns = [
    path('', include(router.urls)),
]

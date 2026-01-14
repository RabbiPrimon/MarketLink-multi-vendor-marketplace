from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepairOrderViewSet, payment_webhook

router = DefaultRouter()
router.register(r'', RepairOrderViewSet)

app_name = 'orders'

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/payment/', payment_webhook, name='payment_webhook'),
]

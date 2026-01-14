from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/vendors/', include('vendors.urls')),
    path('api/orders/', include('orders.urls')),
    path('api-auth/', include('rest_framework.urls')),  # DRF browsable API login
]

from django.db import models
from django.conf import settings


class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class Service(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='variants')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} - ${self.price}"

    def is_available(self):
        return self.stock > 0

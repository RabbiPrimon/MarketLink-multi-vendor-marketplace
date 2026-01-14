import uuid
from django.db import models
from django.conf import settings


class RepairOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey('vendors.VendorProfile', on_delete=models.CASCADE, related_name='orders')
    variant = models.ForeignKey('vendors.ServiceVariant', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.name}"

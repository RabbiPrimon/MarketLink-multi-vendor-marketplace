from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch

from .models import RepairOrder
from vendors.models import VendorProfile, Service, ServiceVariant

User = get_user_model()


class RepairOrderModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            name='Customer',
            password='password123',
            role='customer'
        )
        self.vendor_user = User.objects.create_user(
            email='vendor@example.com',
            name='Vendor',
            password='password123',
            role='vendor'
        )
        self.vendor_profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        self.service = Service.objects.create(
            vendor=self.vendor_profile,
            name='Oil Change',
            description='Change engine oil'
        )
        self.variant = ServiceVariant.objects.create(
            service=self.service,
            price=Decimal('50.00'),
            estimated_minutes=30,
            stock=5
        )

    def test_create_repair_order(self):
        order = RepairOrder.objects.create(
            customer=self.customer,
            vendor=self.vendor_profile,
            variant=self.variant,
            total_amount=self.variant.price
        )
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.vendor, self.vendor_profile)
        self.assertEqual(order.variant, self.variant)
        self.assertEqual(order.total_amount, Decimal('50.00'))
        self.assertEqual(order.status, 'pending')


class RepairOrderAPITest(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            name='Customer',
            password='password123',
            role='customer'
        )
        self.vendor_user = User.objects.create_user(
            email='vendor@example.com',
            name='Vendor',
            password='password123',
            role='vendor'
        )
        self.vendor_profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        self.service = Service.objects.create(
            vendor=self.vendor_profile,
            name='Oil Change',
            description='Change engine oil'
        )
        self.variant = ServiceVariant.objects.create(
            service=self.service,
            price=Decimal('50.00'),
            estimated_minutes=30,
            stock=5
        )
        self.client.force_authenticate(user=self.customer)

    def test_create_repair_order(self):
        url = reverse('orders:repairorder-list')
        data = {
            'variant': self.variant.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RepairOrder.objects.count(), 1)
        order = RepairOrder.objects.first()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.total_amount, Decimal('50.00'))

    def test_create_order_out_of_stock(self):
        self.variant.stock = 0
        self.variant.save()
        url = reverse('orders:repairorder-list')
        data = {
            'variant': self.variant.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(WEBHOOK_SECRET='test-secret')
    def test_payment_webhook_idempotency(self):
        order = RepairOrder.objects.create(
            customer=self.customer,
            vendor=self.vendor_profile,
            variant=self.variant,
            total_amount=self.variant.price
        )
        url = reverse('orders:payment_webhook')
        data = {
            'event_id': 'test-event-123',
            'order_id': str(order.order_id),
            'amount': '50.00',
            'status': 'paid'
        }
        import json
        import hmac
        import hashlib
        body = json.dumps(data).encode()
        signature = hmac.new(
            'test-secret'.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        # First request
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')

        # Second request with same event_id (should be idempotent)
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, 200)
        # Status should remain paid
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')

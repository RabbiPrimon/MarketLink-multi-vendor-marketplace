from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal

from .models import VendorProfile, Service, ServiceVariant

User = get_user_model()


class VendorModelTest(TestCase):
    def setUp(self):
        self.vendor_user = User.objects.create_user(
            email='vendor@example.com',
            name='Vendor',
            password='password123',
            role='vendor'
        )

    def test_create_vendor_profile(self):
        profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        self.assertEqual(profile.business_name, 'Test Shop')
        self.assertEqual(profile.user, self.vendor_user)

    def test_create_service(self):
        profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        service = Service.objects.create(
            vendor=profile,
            name='Oil Change',
            description='Change engine oil'
        )
        self.assertEqual(service.name, 'Oil Change')
        self.assertEqual(service.vendor, profile)

    def test_create_service_variant(self):
        profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        service = Service.objects.create(
            vendor=profile,
            name='Oil Change',
            description='Change engine oil'
        )
        variant = ServiceVariant.objects.create(
            service=service,
            price=Decimal('50.00'),
            estimated_minutes=30,
            stock=5
        )
        self.assertEqual(variant.price, Decimal('50.00'))
        self.assertEqual(variant.stock, 5)
        self.assertTrue(variant.is_available())

    def test_service_variant_out_of_stock(self):
        profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        service = Service.objects.create(
            vendor=profile,
            name='Oil Change',
            description='Change engine oil'
        )
        variant = ServiceVariant.objects.create(
            service=service,
            price=Decimal('50.00'),
            estimated_minutes=30,
            stock=0
        )
        self.assertFalse(variant.is_available())


class VendorAPITest(APITestCase):
    def setUp(self):
        self.vendor_user = User.objects.create_user(
            email='vendor@example.com',
            name='Vendor',
            password='password123',
            role='vendor'
        )
        self.client.force_authenticate(user=self.vendor_user)

    def test_create_vendor_profile(self):
        url = reverse('vendors:vendorprofile-list')
        data = {
            'business_name': 'My Shop',
            'address': '456 Shop St'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VendorProfile.objects.count(), 1)

    def test_create_service(self):
        profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        url = reverse('vendors:service-list')
        data = {
            'name': 'Brake Repair',
            'description': 'Fix car brakes'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 1)

    def test_create_service_variant(self):
        profile = VendorProfile.objects.create(
            user=self.vendor_user,
            business_name='Test Shop',
            address='123 Test St'
        )
        service = Service.objects.create(
            vendor=profile,
            name='Oil Change',
            description='Change engine oil'
        )
        url = reverse('vendors:servicevariant-list')
        data = {
            'service': service.id,
            'price': '75.00',
            'estimated_minutes': 45,
            'stock': 10
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceVariant.objects.count(), 1)

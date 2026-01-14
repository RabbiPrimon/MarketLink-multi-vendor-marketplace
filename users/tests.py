from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='password123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.check_password('password123'))

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='password123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class UserAPITest(APITestCase):
    def test_register_user(self):
        url = reverse('users:register')
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'role': 'customer',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_login_user(self):
        User.objects.create_user(
            email='login@example.com',
            name='Login User',
            password='password123'
        )
        url = reverse('users:login')
        data = {
            'email': 'login@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

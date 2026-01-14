from rest_framework import serializers
from .models import VendorProfile, Service, ServiceVariant


class VendorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'business_name', 'address', 'is_active', 'user_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'vendor', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'vendor', 'created_at', 'updated_at']


class ServiceVariantSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = ServiceVariant
        fields = ['id', 'service', 'price', 'estimated_minutes', 'stock', 'service_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'service', 'created_at', 'updated_at']

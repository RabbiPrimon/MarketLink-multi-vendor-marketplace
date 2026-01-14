from rest_framework import serializers
from .models import RepairOrder
from vendors.models import ServiceVariant


class RepairOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)
    service_name = serializers.CharField(source='variant.service.name', read_only=True)
    variant_details = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = [
            'order_id', 'customer', 'vendor', 'variant', 'status', 'total_amount',
            'customer_name', 'vendor_name', 'service_name', 'variant_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_id', 'customer', 'total_amount', 'created_at', 'updated_at']

    def get_variant_details(self, obj):
        return {
            'price': obj.variant.price,
            'estimated_minutes': obj.variant.estimated_minutes,
        }

    def create(self, validated_data):
        # Set total_amount from variant price
        variant = validated_data['variant']
        validated_data['total_amount'] = variant.price
        return super().create(validated_data)


class RepairOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrder
        fields = ['variant']

    def validate_variant(self, value):
        if not value.is_available():
            raise serializers.ValidationError("This service variant is not available.")
        return value

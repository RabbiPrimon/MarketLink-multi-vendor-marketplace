from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import VendorProfile, Service, ServiceVariant
from .serializers import VendorProfileSerializer, ServiceSerializer, ServiceVariantSerializer


class VendorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = VendorProfile.objects.all()

    def get_queryset(self):
        return VendorProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.all()

    def get_queryset(self):
        return Service.objects.filter(vendor__user=self.request.user)

    def perform_create(self, serializer):
        vendor = get_object_or_404(VendorProfile, user=self.request.user)
        serializer.save(vendor=vendor)


class ServiceVariantViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceVariantSerializer
    permission_classes = [IsAuthenticated]
    queryset = ServiceVariant.objects.all()

    def get_queryset(self):
        return ServiceVariant.objects.filter(service__vendor__user=self.request.user)

    def perform_create(self, serializer):
        service = get_object_or_404(Service, id=self.request.data.get('service'), vendor__user=self.request.user)
        serializer.save(service=service)

import hmac
import hashlib
import redis
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import RepairOrder
from .serializers import RepairOrderSerializer, RepairOrderCreateSerializer
from .tasks import process_order


class RepairOrderViewSet(viewsets.ModelViewSet):
    serializer_class = RepairOrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = RepairOrder.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return RepairOrder.objects.filter(customer=user)
        elif user.role == 'vendor':
            return RepairOrder.objects.filter(vendor__user=user)
        return RepairOrder.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return RepairOrderCreateSerializer
        return RepairOrderSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            variant = serializer.validated_data['variant']
            # Use Redis lock to prevent double-booking
            r = redis.from_url(settings.REDIS_URL)
            lock_key = f"variant_lock:{variant.id}"
            with r.lock(lock_key, timeout=10):
                if variant.stock <= 0:
                    raise ValueError("Service variant is out of stock")
                variant.stock -= 1
                variant.save()
                serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        order = self.get_object()
        if order.customer != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        if order.status != 'pending':
            return Response({'error': 'Order is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)

        # Simulate payment URL generation
        payment_url = f"https://payment.example.com/pay/{order.order_id}"
        return Response({'payment_url': payment_url})


@csrf_exempt
@require_POST
def payment_webhook(request):
    """
    Handle payment webhook with idempotency and signature validation.
    """
    # Get webhook secret from settings
    webhook_secret = settings.WEBHOOK_SECRET

    # Validate signature
    signature = request.META.get('HTTP_X_SIGNATURE')
    if not signature:
        return JsonResponse({'error': 'Missing signature'}, status=400)

    body = request.body.decode('utf-8')
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Parse webhook data
    import json
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    event_id = data.get('event_id')
    order_id = data.get('order_id')
    amount = data.get('amount')
    payment_status = data.get('status')

    if not all([event_id, order_id, amount, payment_status]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    # Idempotency check using Redis
    r = redis.from_url(settings.REDIS_URL)
    idempotency_key = f"webhook:{event_id}"
    if r.get(idempotency_key):
        return JsonResponse({'message': 'Already processed'}, status=200)

    try:
        order = RepairOrder.objects.get(order_id=order_id)
    except RepairOrder.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    # Validate amount
    if float(amount) != float(order.total_amount):
        return JsonResponse({'error': 'Amount mismatch'}, status=400)

    if payment_status == 'paid':
        with transaction.atomic():
            order.status = 'paid'
            order.save()
            # Set idempotency key
            r.set(idempotency_key, '1', ex=86400)  # Expire in 24 hours
            # Enqueue background task
            process_order.delay(order.id)
        return JsonResponse({'message': 'Payment processed successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Payment not successful'}, status=400)

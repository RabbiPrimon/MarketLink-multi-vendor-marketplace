from celery import shared_task
from .models import RepairOrder


@shared_task
def process_order(order_id):
    """
    Background task to process the order after payment.
    In a real app, this would send invoice, notify vendor, etc.
    """
    try:
        order = RepairOrder.objects.get(id=order_id)
        # Simulate processing
        order.status = 'processing'
        order.save()
        # Here you would send invoice email, notify vendor, etc.
        print(f"Processing order {order.order_id}")
    except RepairOrder.DoesNotExist:
        print(f"Order {order_id} not found")

from store.signals import order_created
from django.dispatch import receiver

@receiver(order_created)
def on_order_created(sender, **kwargs):
    order = kwargs['order']
    print("="*20)
    print(f"Order created: {order.id}")
    print("="*20)
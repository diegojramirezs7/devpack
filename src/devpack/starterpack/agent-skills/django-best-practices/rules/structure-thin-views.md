---
title: Keep Business Logic Out of Views
impact: HIGH
impactDescription: improves testability, reusability, and maintainability
tags: structure, views, services, business-logic, separation-of-concerns
---

## Keep Business Logic Out of Views

Views should be thin — they handle request/response. Business logic belongs in services or model methods.

**Incorrect (thick view with business logic):**

```python
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    if cart.total > request.user.profile.credit_limit:
        raise ValidationError("Over credit limit")
    order = Order.objects.create(user=request.user, total=cart.total)
    for item in cart.items.all():
        OrderItem.objects.create(order=order, product=item.product, qty=item.qty)
    cart.items.all().delete()
    send_order_confirmation.delay(order.id)
    return redirect('order-detail', order.id)
```

**Correct (thin view, fat service):**

```python
# services/orders.py
def create_order_from_cart(user):
    cart = Cart.objects.get(user=user)
    if cart.total > user.profile.credit_limit:
        raise ValidationError("Over credit limit")
    order = Order.objects.create(user=user, total=cart.total)
    OrderItem.objects.bulk_create([
        OrderItem(order=order, product=item.product, qty=item.qty)
        for item in cart.items.select_related('product')
    ])
    cart.items.all().delete()
    send_order_confirmation.delay(order.id)
    return order

# views.py
def create_order(request):
    order = create_order_from_cart(request.user)
    return redirect('order-detail', order.id)
```

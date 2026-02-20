---
title: Write Tests from the Start
impact: CRITICAL
impactDescription: catches regressions early and enables confident refactoring
tags: testing, test-case, views, services, models
---

## Write Tests from the Start

Every model, view, and service function should have tests. Django's test framework makes this easy.

**Correct:**

```python
from django.test import TestCase, Client
from django.urls import reverse

class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='pass')
        self.product = Product.objects.create(name='Widget', price=10.00)

    def test_create_order_from_cart(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, qty=2)
        order = create_order_from_cart(self.user)
        self.assertEqual(order.total, 20.00)
        self.assertEqual(order.items.count(), 1)

class OrderViewTest(TestCase):
    def test_order_list_requires_auth(self):
        response = self.client.get(reverse('orders:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
```

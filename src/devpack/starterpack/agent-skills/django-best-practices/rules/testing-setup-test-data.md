---
title: Use setUpTestData for Expensive Setup
impact: MODERATE
impactDescription: creates data once per test class instead of per test method
tags: testing, setup, performance, test-data
---

## Use setUpTestData for Expensive Setup

`setUpTestData` creates data once per test class (not per test method), significantly speeding up tests.

**Correct:**

```python
class ProductViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Created once for ALL tests in this class (faster)
        cls.category = Category.objects.create(name='Electronics')
        cls.products = ProductFactory.create_batch(50, category=cls.category)

    def test_product_list(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(len(response.context['products']), 50)
```

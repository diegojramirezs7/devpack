---
title: Use App-Level urls.py and Include in Root
impact: MODERATE
impactDescription: keeps URL configuration modular and maintainable
tags: structure, urls, routing, modularity
---

## Use App-Level urls.py and Include in Root

Don't put all URL patterns in a single file.

**Incorrect (everything in one file):**

```python
# config/urls.py
urlpatterns = [
    path('users/', user_list),
    path('users/<int:pk>/', user_detail),
    path('products/', product_list),
    path('orders/', order_list),
    # ... hundreds of URLs
]
```

**Correct (modular URL configuration):**

```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.accounts.urls')),
    path('products/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
]

# apps/accounts/urls.py
app_name = 'accounts'
urlpatterns = [
    path('', views.user_list, name='list'),
    path('<int:pk>/', views.user_detail, name='detail'),
]
```

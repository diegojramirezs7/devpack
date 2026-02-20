# Django Best Practices

Comprehensive best practices guide for Django applications, designed for AI agents and developers. Contains 60+ rules across 9 categories, prioritized by impact from CRITICAL to LOW. Each rule includes explanations and code examples comparing incorrect vs. correct implementations.

> **Note:** This document is optimized for AI agents (Claude Code, Cursor, Copilot, etc.) to follow when generating, reviewing, or refactoring Django codebases. Humans will also find it useful as a reference.

---

## 1. Database & ORM Performance

The ORM is where most Django performance issues originate. Fixing query patterns yields the largest gains.

### 1.1 Eliminate N+1 Queries with select_related and prefetch_related

**Impact: CRITICAL**

The N+1 problem is Django's #1 performance killer. Every time you access a related object in a loop without prefetching, Django issues a separate query.

**Incorrect:**

```python
# N+1: 1 query for books + N queries for each book's author
books = Book.objects.all()
for book in books:
    print(book.author.name)  # Separate query per book!
```

**Correct:**

```python
# ForeignKey / OneToOne → use select_related (SQL JOIN, single query)
books = Book.objects.select_related('author').all()
for book in books:
    print(book.author.name)  # No additional query

# ManyToMany / reverse FK → use prefetch_related (separate query, joined in Python)
authors = Author.objects.prefetch_related('books').all()
for author in authors:
    print(list(author.books.all()))  # No additional query
```

**When to use which:**

- `select_related`: ForeignKey, OneToOneField — uses SQL JOIN, single query.
- `prefetch_related`: ManyToManyField, reverse ForeignKey — uses separate queries + Python join.

### 1.2 Combine select_related Inside prefetch_related with Prefetch Objects

**Impact: HIGH**

When prefetched objects themselves have ForeignKey relationships, use `Prefetch` with a custom queryset to avoid a second layer of N+1.

**Incorrect:**

```python
# Prefetches chapters, but each chapter.editor triggers another query
books = Book.objects.prefetch_related('chapters').all()
for book in books:
    for chapter in book.chapters.all():
        print(chapter.editor.name)  # N+1 inside N+1!
```

**Correct:**

```python
from django.db.models import Prefetch

books = Book.objects.prefetch_related(
    Prefetch('chapters', queryset=Chapter.objects.select_related('editor'))
).all()
for book in books:
    for chapter in book.chapters.all():
        print(chapter.editor.name)  # Already loaded
```

### 1.3 Use only() and defer() to Limit Fetched Columns

**Impact: HIGH**

Avoid fetching large text/binary columns when you only need a few fields.

**Incorrect:**

```python
# Fetches ALL columns including large body text
posts = Post.objects.all()
for post in posts:
    print(post.title)
```

**Correct:**

```python
# Only fetch the columns you need
posts = Post.objects.only('id', 'title', 'created_at')
for post in posts:
    print(post.title)

# Or defer the expensive ones
posts = Post.objects.defer('body', 'raw_html')
```

### 1.4 Use values() or values_list() When You Don't Need Model Instances

**Impact: HIGH**

If you only need raw data (for serialization, aggregation, or template rendering), skip model instantiation entirely.

**Incorrect:**

```python
emails = [user.email for user in User.objects.all()]
```

**Correct:**

```python
emails = list(User.objects.values_list('email', flat=True))
```

### 1.5 Use F() Expressions for Database-Level Operations

**Impact: MODERATE**

Avoid pulling data into Python just to update it. Use `F()` to perform operations at the database level, preventing race conditions.

**Incorrect:**

```python
product = Product.objects.get(id=1)
product.views += 1  # Race condition if concurrent requests
product.save()
```

**Correct:**

```python
from django.db.models import F

Product.objects.filter(id=1).update(views=F('views') + 1)
```

### 1.6 Use bulk_create and bulk_update for Batch Operations

**Impact: MODERATE**

Avoid saving objects one by one in a loop.

**Incorrect:**

```python
for item in items_data:
    Item.objects.create(name=item['name'], price=item['price'])
# N insert queries
```

**Correct:**

```python
items = [Item(name=d['name'], price=d['price']) for d in items_data]
Item.objects.bulk_create(items, batch_size=1000)

# For updates:
for item in items:
    item.price = item.price * 1.1
Item.objects.bulk_update(items, ['price'], batch_size=1000)
```

### 1.7 Add Database Indexes on Frequently Filtered/Ordered Fields

**Impact: HIGH**

Missing indexes cause full table scans on large tables.

**Incorrect:**

```python
class Order(models.Model):
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_email = models.EmailField()
    # No indexes — queries filtering by status or created_at are slow
```

**Correct:**

```python
class Order(models.Model):
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    customer_email = models.EmailField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),  # Composite index
            models.Index(
                fields=['status'],
                condition=models.Q(status='pending'),
                name='pending_orders_idx',  # Partial index
            ),
        ]
```

### 1.8 Use exists() and count() Instead of Evaluating Entire QuerySets

**Impact: MODERATE**

Don't load all objects into memory just to check if something exists or count rows.

**Incorrect:**

```python
if len(User.objects.filter(email=email)):  # Loads ALL matching users into memory
    raise ValidationError("Email taken")

total = len(Order.objects.filter(status='pending'))  # Loads all rows
```

**Correct:**

```python
if User.objects.filter(email=email).exists():  # SELECT 1 ... LIMIT 1
    raise ValidationError("Email taken")

total = Order.objects.filter(status='pending').count()  # SELECT COUNT(*)
```

### 1.9 Use iterator() for Large QuerySets

**Impact: MODERATE**

When processing large datasets, `iterator()` avoids caching the entire queryset in memory.

```python
# Process millions of rows without memory issues
for order in Order.objects.filter(status='completed').iterator(chunk_size=2000):
    process_order(order)
```

### 1.10 Use Database Connection Pooling

**Impact: HIGH**

Django creates a new database connection per request by default. Use connection pooling for high-traffic apps.

```python
# Django 5.1+ built-in connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'pool': {
                'min_size': 2,
                'max_size': 10,
            },
        },
    }
}
```

---

## 2. Security

Django is secure by default, but misconfiguration is the #1 cause of Django security vulnerabilities.

### 2.1 Never Run DEBUG = True in Production

**Impact: CRITICAL**

Debug mode exposes full tracebacks, settings, and environment details to anyone who triggers an error.

**Incorrect:**

```python
# settings.py
DEBUG = True  # In production — exposes secrets, paths, SQL queries
```

**Correct:**

```python
import os

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
```

### 2.2 Keep SECRET_KEY Out of Source Control

**Impact: CRITICAL**

The `SECRET_KEY` is used for cryptographic signing (sessions, tokens, password resets). If leaked, attackers can forge sessions.

**Incorrect:**

```python
SECRET_KEY = 'django-insecure-abc123hardcoded'
```

**Correct:**

```python
import os

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # Fail loudly if not set
```

### 2.3 Configure ALLOWED_HOSTS Properly

**Impact: CRITICAL**

An empty or wildcard `ALLOWED_HOSTS` enables HTTP Host header attacks.

**Incorrect:**

```python
ALLOWED_HOSTS = ['*']  # Accepts any Host header
```

**Correct:**

```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
# e.g., DJANGO_ALLOWED_HOSTS=example.com,www.example.com
```

### 2.4 Enable HTTPS Security Headers

**Impact: HIGH**

Always enforce HTTPS and set security headers in production.

```python
# Production settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### 2.5 Always Validate and Sanitize User Input

**Impact: CRITICAL**

Never pass unsanitized user input to raw SQL, ORM extras, or template rendering.

**Incorrect:**

```python
# SQL injection risk
User.objects.raw(f"SELECT * FROM auth_user WHERE email = '{email}'")

# Template XSS risk
return HttpResponse(f"<h1>Hello {user_input}</h1>")
```

**Correct:**

```python
# Parameterized queries
User.objects.raw("SELECT * FROM auth_user WHERE email = %s", [email])

# Or just use the ORM
User.objects.filter(email=email)

# Use templates with auto-escaping (on by default)
return render(request, 'hello.html', {'name': user_input})
```

### 2.6 Use Django's CSRF Protection

**Impact: HIGH**

Never disable CSRF middleware. Use `{% csrf_token %}` in every POST form.

**Incorrect:**

```python
@csrf_exempt  # Don't do this unless you have a very specific API reason
def my_view(request):
    ...
```

**Correct:**

```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

For APIs (DRF), use token or session authentication — both handle CSRF properly.

### 2.7 Use Django's Password Validation and Hashing

**Impact: HIGH**

Never store plaintext passwords. Use Django's built-in auth system.

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 2.8 Protect Against Mass Assignment

**Impact: MODERATE**

Never blindly pass request data to model creation.

**Incorrect:**

```python
User.objects.create(**request.POST.dict())  # User can set is_superuser=True!
```

**Correct:**

```python
# Use Django forms or serializers to whitelist fields
form = UserRegistrationForm(request.POST)
if form.is_valid():
    form.save()
```

### 2.9 Run the Deployment Checklist

**Impact: MODERATE**

Django includes a built-in security checker.

```bash
python manage.py check --deploy
```

This warns about missing security settings like `SECURE_SSL_REDIRECT`, `CSRF_COOKIE_SECURE`, etc.

---

## 3. Project Structure & Code Organization

A clean, consistent project structure prevents code rot as projects scale.

### 3.1 Use a Custom User Model from Day One

**Impact: CRITICAL**

Changing the user model after initial migration is extremely painful. Always start with a custom model.

**Incorrect:**

```python
# Using Django's built-in User model directly
from django.contrib.auth.models import User
```

**Correct:**

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass  # Add custom fields later as needed

# settings.py
AUTH_USER_MODEL = 'accounts.User'
```

Always reference the user model dynamically:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
```

### 3.2 Split Settings by Environment

**Impact: HIGH**

Don't use a single settings.py for dev and production.

```
config/
├── settings/
│   ├── __init__.py
│   ├── base.py          # Shared settings
│   ├── development.py   # DEBUG=True, local DB
│   ├── production.py    # Security hardened
│   └── test.py          # Fast test settings
```

```python
# config/settings/development.py
from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Use environment variables to select: `DJANGO_SETTINGS_MODULE=config.settings.production`

### 3.3 Keep Business Logic Out of Views

**Impact: HIGH**

Views should be thin — they handle request/response. Business logic belongs in services or model methods.

**Incorrect:**

```python
# views.py — thick view with business logic
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

**Correct:**

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

# views.py — thin view
def create_order(request):
    order = create_order_from_cart(request.user)
    return redirect('order-detail', order.id)
```

### 3.4 Organize Apps by Domain, One Responsibility Per App

**Impact: MODERATE**

Each app should have a clear, focused purpose.

```
project/
├── apps/
│   ├── accounts/     # User auth, profiles
│   ├── orders/       # Order management
│   ├── products/     # Product catalog
│   └── notifications/  # Email, push notifications
├── config/
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

Each app should be independently testable and potentially reusable.

### 3.5 Use App-Level urls.py and Include in Root

**Impact: MODERATE**

Don't put all URL patterns in a single file.

**Incorrect:**

```python
# config/urls.py — everything in one file
urlpatterns = [
    path('users/', user_list),
    path('users/<int:pk>/', user_detail),
    path('products/', product_list),
    path('orders/', order_list),
    # ... hundreds of URLs
]
```

**Correct:**

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

### 3.6 Use Meaningful Related Names

**Impact: LOW**

Always set `related_name` on ForeignKey and ManyToMany fields to make reverse lookups readable.

**Incorrect:**

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # Access: post.comment_set.all() — unclear
```

**Correct:**

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # Access: post.comments.all() — clear and readable
```

---

## 4. Caching

Caching is the single most impactful performance optimization after fixing N+1 queries.

### 4.1 Use a Proper Cache Backend in Production

**Impact: CRITICAL**

The default in-memory cache does not persist across processes.

**Incorrect:**

```python
# Default — local memory, per-process, no sharing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

**Correct:**

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'myapp',
        'TIMEOUT': 300,  # Default 5 minute TTL
    }
}
```

### 4.2 Cache Expensive QuerySets and Computations

**Impact: HIGH**

Cache database queries and computed results that don't change frequently.

```python
from django.core.cache import cache

def get_popular_products():
    key = 'popular_products'
    products = cache.get(key)
    if products is None:
        products = list(
            Product.objects.filter(is_active=True)
            .annotate(order_count=Count('orderitem'))
            .order_by('-order_count')[:20]
        )
        cache.set(key, products, timeout=60 * 15)  # 15 minutes
    return products
```

### 4.3 Use Per-View Caching for Read-Heavy Pages

**Impact: MODERATE**

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/list.html', {'products': products})
```

### 4.4 Use Template Fragment Caching for Partial Content

**Impact: MODERATE**

Cache expensive template blocks instead of entire pages.

```django
{% load cache %}

{% cache 600 sidebar request.user.id %}
    {# Expensive sidebar content #}
    {% for notification in notifications %}
        <div>{{ notification.message }}</div>
    {% endfor %}
{% endcache %}
```

### 4.5 Invalidate Cache Properly

**Impact: HIGH**

Stale caches cause subtle bugs. Use signals or explicit invalidation.

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, **kwargs):
    cache.delete('popular_products')
    cache.delete('product_categories')
```

---

## 5. Static Files & Media

### 5.1 Never Serve Static Files with Django in Production

**Impact: CRITICAL**

Django's static file serving is single-threaded and not designed for production.

**Incorrect:**

```python
# In production — using Django to serve statics
if DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# ^^^ This should NEVER be the production strategy
```

**Correct options:**

```python
# Option 1: WhiteNoise (simple, works well for most apps)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add right after SecurityMiddleware
    # ...
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Option 2: CDN / object storage (S3, GCS, etc.)
# Use django-storages for S3/GCS
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

### 5.2 Always Run collectstatic in Deployment

**Impact: HIGH**

```bash
python manage.py collectstatic --noinput
```

Configure `STATIC_ROOT` to point to the directory your web server or WhiteNoise serves from.

### 5.3 Validate and Limit User-Uploaded Files

**Impact: HIGH**

Never trust user uploads. Validate file types, sizes, and store them outside of your application code.

```python
from django.core.validators import FileExtensionValidator

class Document(models.Model):
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'txt'])],
    )

# In settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

### 5.4 Use Content-Hash File Names for Cache Busting

**Impact: MODERATE**

```python
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
# Produces filenames like: css/style.a1b2c3d4.css
```

---

## 6. Testing

### 6.1 Write Tests from the Start

**Impact: CRITICAL**

Every model, view, and service function should have tests. Django's test framework makes this easy.

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

### 6.2 Use Factories Instead of Fixtures

**Impact: HIGH**

Fixtures are brittle and hard to maintain. Use factory_boy for test data.

**Incorrect:**

```python
# fixtures/test_data.json — breaks when models change
[{"model": "accounts.user", "pk": 1, "fields": {"username": "test"}}]
```

**Correct:**

```python
# tests/factories.py
import factory
from apps.accounts.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')

# In tests
user = UserFactory()
admin = UserFactory(is_staff=True, is_superuser=True)
```

### 6.3 Use setUpTestData for Expensive Setup

**Impact: MODERATE**

`setUpTestData` creates data once per test class (not per test method), significantly speeding up tests.

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

### 6.4 Use an In-Memory SQLite Database for Tests When Possible

**Impact: MODERATE**

```python
# config/settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']  # Faster hashing in tests
```

Note: If you rely on PostgreSQL-specific features (JSONField lookups, array fields, full-text search), test against PostgreSQL instead.

---

## 7. Async & Background Tasks

### 7.1 Offload Long-Running Work to Background Tasks

**Impact: CRITICAL**

Never block a request to send emails, generate reports, or call external APIs.

**Incorrect:**

```python
def register(request):
    user = User.objects.create_user(...)
    send_mail('Welcome!', 'Thanks for joining.', 'no-reply@example.com', [user.email])
    generate_welcome_pdf(user)  # Takes 5 seconds!
    return redirect('dashboard')
```

**Correct:**

```python
# tasks.py (Celery)
from celery import shared_task

@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)
    send_mail('Welcome!', 'Thanks for joining.', 'no-reply@example.com', [user.email])

@shared_task
def generate_welcome_pdf(user_id):
    ...

# views.py
def register(request):
    user = User.objects.create_user(...)
    send_welcome_email.delay(user.id)  # Non-blocking
    generate_welcome_pdf.delay(user.id)  # Non-blocking
    return redirect('dashboard')
```

### 7.2 Pass IDs, Not Objects, to Celery Tasks

**Impact: HIGH**

Celery serializes task arguments. Pass database IDs and re-fetch inside the task to avoid stale data and serialization issues.

**Incorrect:**

```python
@shared_task
def process_order(order):  # Passing a model instance — breaks serialization
    order.status = 'processed'
    order.save()
```

**Correct:**

```python
@shared_task
def process_order(order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'processed'
    order.save()
```

### 7.3 Use Async Views for I/O-Bound Operations

**Impact: MODERATE**

Django 4.1+ supports native async views. Use them when calling external APIs or performing concurrent I/O.

```python
import httpx

async def dashboard(request):
    async with httpx.AsyncClient() as client:
        weather, news = await asyncio.gather(
            client.get('https://api.weather.com/current'),
            client.get('https://api.news.com/headlines'),
        )
    return render(request, 'dashboard.html', {
        'weather': weather.json(),
        'news': news.json(),
    })
```

Note: The ORM is not fully async yet. Wrap sync ORM calls with `sync_to_async`:

```python
from asgiref.sync import sync_to_async

@sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)
```

---

## 8. Configuration & Deployment

### 8.1 Use Environment Variables for All Configuration

**Impact: CRITICAL**

Never hardcode database credentials, API keys, or secrets.

```python
import os

# Or use django-environ / python-decouple
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### 8.2 Use Gunicorn or Uvicorn Behind a Reverse Proxy

**Impact: CRITICAL**

Never use `manage.py runserver` in production.

```bash
# WSGI (synchronous)
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000

# ASGI (if using async views or WebSockets)
uvicorn config.asgi:application --workers 4 --host 0.0.0.0 --port 8000
```

Put Nginx or a load balancer in front for SSL termination, static files, and connection management.

### 8.3 Configure Logging Properly

**Impact: HIGH**

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING',  # Set to DEBUG to see all SQL queries
        },
    },
}
```

### 8.4 Use Health Check Endpoints

**Impact: MODERATE**

```python
# health/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        connection.ensure_connection()
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)
```

### 8.5 Pin Dependencies and Use Lock Files

**Impact: HIGH**

```
# requirements/base.txt
Django==5.2.*
psycopg2-binary==2.9.*
celery==5.4.*

# requirements/production.txt
-r base.txt
gunicorn==22.*
django-redis==5.*
sentry-sdk==2.*
```

Or better yet, use `pyproject.toml` with `uv`, `poetry`, or `pip-tools` for deterministic builds.

---

## 9. Development Tooling & Quality

### 9.1 Use django-debug-toolbar in Development

**Impact: HIGH**

Essential for spotting N+1 queries, slow templates, and cache misses.

```python
# config/settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### 9.2 Use Linting and Formatting Tools

**Impact: MODERATE**

Consistent code formatting reduces review friction and prevents style debates.

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "DJ"]  # DJ = Django-specific rules

[tool.ruff.lint.isort]
known-first-party = ["apps"]
```

### 9.3 Use Type Hints

**Impact: LOW**

Type hints improve IDE support and catch bugs early. Use `django-stubs` for Django-specific types.

```python
from django.http import HttpRequest, HttpResponse

def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {'product': product})
```

### 9.4 Use Migrations Responsibly

**Impact: HIGH**

- Never edit migration files after they've been applied in production.
- Squash migrations periodically to keep the history manageable.
- Use `RunPython` for data migrations, keeping them reversible.
- Always add `db_index` to fields you query by, but be aware that adding indexes on large tables locks the table.

```python
# Data migration example — always provide a reverse function
from django.db import migrations

def populate_slug(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for post in Post.objects.filter(slug=''):
        post.slug = slugify(post.title)
        post.save(update_fields=['slug'])

def reverse_slug(apps, schema_editor):
    pass  # Slug removal is safe to skip

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_slug, reverse_slug),
    ]
```

### 9.5 Use Continuous Integration

**Impact: HIGH**

Run tests, linting, and type checking on every commit.

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements/test.txt
      - run: ruff check .
      - run: python manage.py test --settings=config.settings.test
```

---

## Quick Reference: Impact Priority

| Priority | Category | Rule |
|----------|----------|------|
| CRITICAL | Database | Eliminate N+1 queries (select_related / prefetch_related) |
| CRITICAL | Security | DEBUG = False in production |
| CRITICAL | Security | SECRET_KEY in env vars |
| CRITICAL | Security | ALLOWED_HOSTS configured |
| CRITICAL | Security | Validate all user input |
| CRITICAL | Structure | Custom User model from day one |
| CRITICAL | Caching | Use Redis/Memcached in production |
| CRITICAL | Static | Never serve statics with Django in production |
| CRITICAL | Async | Offload long tasks to background workers |
| CRITICAL | Deploy | Use Gunicorn/Uvicorn, not runserver |
| CRITICAL | Deploy | Environment variables for all config |
| HIGH | Database | Use Prefetch objects for nested relations |
| HIGH | Database | Use only()/defer() for column limiting |
| HIGH | Database | Add indexes on filtered/ordered fields |
| HIGH | Database | Use connection pooling |
| HIGH | Security | Enable HTTPS headers (HSTS, secure cookies) |
| HIGH | Security | Use CSRF protection |
| HIGH | Security | Use password validators |
| HIGH | Structure | Split settings by environment |
| HIGH | Structure | Thin views, fat services |
| HIGH | Caching | Cache expensive querysets |
| HIGH | Caching | Invalidate caches on write |
| HIGH | Static | Validate user uploads |
| HIGH | Testing | Use factory_boy instead of fixtures |
| HIGH | Async | Pass IDs to Celery, not objects |
| HIGH | Deploy | Configure logging |
| HIGH | Deploy | Pin dependencies |
| HIGH | Tooling | Use django-debug-toolbar |
| HIGH | Tooling | Use CI pipelines |
| HIGH | Tooling | Manage migrations responsibly |
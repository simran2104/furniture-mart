from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    description = models.TextField(blank=True)
    class Meta:
        ordering = ["name"]
    def __str__(self): return self.name

class Product(models.Model):
    sku = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=240)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.CharField(max_length=80, default="Sarvotam Collection")
    material = models.CharField(max_length=80)
    colour = models.CharField(max_length=50)
    finish = models.CharField(max_length=80)
    dimensions = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(default="https://images.pexels.com/photos/7166647/pexels-photo-7166647.jpeg?auto=compress&cs=tinysrgb&w=1200")
    image_urls = models.JSONField(default=list, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    review_count = models.PositiveIntegerField(default=0)
    stock_quantity = models.PositiveIntegerField(default=10)
    featured = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)
    customizable = models.BooleanField(default=False)
    assembly_required = models.BooleanField(default=True)
    warranty = models.CharField(max_length=100, default="1 year warranty")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-featured", "-created_at"]
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["category", "price"]), models.Index(fields=["new_arrival"])]
    def __str__(self): return self.name
    @property
    def selling_price(self): return self.discount_price or self.price
    @property
    def discount_percent(self): return round((1 - self.discount_price / self.price) * 100) if self.discount_price else 0
    @property
    def gallery_images(self): return self.image_urls or [self.image_url]

class Enquiry(models.Model):
    STATUS_CHOICES = [("new", "New"), ("contacted", "Contacted"), ("scheduled", "Showroom Visit Scheduled"), ("completed", "Completed"), ("closed", "Closed")]
    reference = models.CharField(max_length=30, unique=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    subject = models.CharField(max_length=160, blank=True)
    message = models.TextField()
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

class AnalyticsEvent(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=100, blank=True, db_index=True)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

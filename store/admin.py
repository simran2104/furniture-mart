from django.contrib import admin
from .models import AnalyticsEvent, Category, Enquiry, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "selling_price", "featured", "popular")
    list_filter = ("category", "material", "featured", "new_arrival", "popular")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "product", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("reference", "name", "email", "phone")

@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "user", "created_at")
    list_filter = ("name", "created_at")

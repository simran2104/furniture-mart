from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("category/<slug:slug>/", views.products, name="category"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("search/", views.products, name="search"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("enquiry/", views.enquiry, name="enquiry"),
    path("contact/", views.contact, name="contact"),
    path("showroom/", views.showroom, name="showroom"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("account/", views.account, name="account"),
    path("analytics/", views.analytics, name="analytics"),
    path("api/analytics/events/", views.analytics_event, name="analytics_event"),
]

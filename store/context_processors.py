from django.conf import settings
from .models import Category

def site_context(request):
    cart = request.session.get("cart", {})
    return {
        "nav_categories": Category.objects.filter(parent__isnull=True)[:6],
        "cart_count": sum(cart.values()),
        "showroom_phone": settings.SHOWROOM_PHONE,
        "showroom_email": settings.SHOWROOM_EMAIL,
    }

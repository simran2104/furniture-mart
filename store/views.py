import json
from datetime import date
from uuid import uuid4
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ContactForm, EnquiryForm
from .models import AnalyticsEvent, Category, Enquiry, Product

HOME_CATEGORY_IMAGES = {
    "Living Room": "https://images.pexels.com/photos/7166647/pexels-photo-7166647.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Bedroom": "https://images.pexels.com/photos/1648768/pexels-photo-1648768.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Kitchen": "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Dining Room": "https://images.pexels.com/photos/8082211/pexels-photo-8082211.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Study Room": "https://images.pexels.com/photos/667838/pexels-photo-667838.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Office": "https://images.pexels.com/photos/3184436/pexels-photo-3184436.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Outdoor": "https://images.pexels.com/photos/157811/pexels-photo-157811.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Storage": "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "Home Furnishing": "https://images.pexels.com/photos/1457847/pexels-photo-1457847.jpeg?auto=compress&cs=tinysrgb&w=1200",
}


def track(request, name, product=None, metadata=None):
    if request.session.session_key is None: request.session.create()
    AnalyticsEvent.objects.create(name=name, user=request.user if request.user.is_authenticated else None, session_key=request.session.session_key, product=product, metadata=metadata or {})

def home(request):
    track(request, "page_view", metadata={"page": "home"})
    categories = list(Category.objects.filter(parent__isnull=True))
    for category in categories:
        category.card_image = HOME_CATEGORY_IMAGES.get(category.name, HOME_CATEGORY_IMAGES["Living Room"])
    return render(request, "store/home.html", {"featured": Product.objects.filter(featured=True)[:8], "new_arrivals": Product.objects.filter(new_arrival=True)[:4], "categories": categories, "hero_image": HOME_CATEGORY_IMAGES["Living Room"]})

def products(request, slug=None):
    query = request.GET.get("q", "").strip()
    category_slug = slug or request.GET.get("category", "")
    qs = Product.objects.select_related("category").all()
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        qs = qs.filter(Q(category=category) | Q(category__parent=category))
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(material__icontains=query) | Q(brand__icontains=query) | Q(sku__icontains=query))
        track(request, "search", metadata={"query": query, "resultsCount": qs.count()})
    material = request.GET.get("material")
    if material: qs = qs.filter(material=material)
    if request.GET.get("new_arrival") == "1": qs = qs.filter(new_arrival=True)
    sort = request.GET.get("sort", "relevance")
    sort_map = {"price_asc": "discount_price", "price_desc": "-discount_price", "newest": "-created_at", "rating": "-rating", "popular": "-popular"}
    if sort in sort_map: qs = qs.order_by(sort_map[sort])
    paginator = Paginator(qs, 24)
    page = paginator.get_page(request.GET.get("page", 1))
    track(request, "category_view" if category else "page_view", metadata={"page": "products", "category": category_slug})
    return render(request, "store/products.html", {"page": page, "category": category, "query": query, "sort": sort, "materials": Product.objects.values_list("material", flat=True).distinct()})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    track(request, "product_view", product, {"category": product.category.name})
    recently = request.session.get("recently_viewed", [])
    request.session["recently_viewed"] = ([product.id] + [item for item in recently if item != product.id])[:6]
    return render(request, "store/product_detail.html", {"product": product})

def cart_items(request):
    cart = request.session.get("cart", {})
    products_by_id = Product.objects.in_bulk([int(key) for key in cart])
    return [(products_by_id[int(key)], quantity) for key, quantity in cart.items() if int(key) in products_by_id]

def cart(request):
    items = cart_items(request)
    total = sum(item.selling_price * quantity for item, quantity in items)
    track(request, "cart_view")
    return render(request, "store/cart.html", {"items": items, "total": total})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_data = request.session.get("cart", {})
    key = str(product_id); cart_data[key] = cart_data.get(key, 0) + int(request.POST.get("quantity", 1))
    request.session["cart"] = cart_data
    track(request, "add_to_cart", product, {"quantity": cart_data[key], "price": float(product.selling_price)})
    messages.success(request, f"{product.name} added to your shortlist cart.")
    return redirect(request.POST.get("next", "cart"))

def update_cart(request, product_id):
    cart_data = request.session.get("cart", {})
    quantity = max(0, int(request.POST.get("quantity", 1)))
    if quantity: cart_data[str(product_id)] = quantity
    else: cart_data.pop(str(product_id), None)
    request.session["cart"] = cart_data
    return redirect("cart")

def remove_from_cart(request, product_id):
    cart_data = request.session.get("cart", {}); cart_data.pop(str(product_id), None); request.session["cart"] = cart_data
    track(request, "remove_from_cart", metadata={"productId": product_id})
    return redirect("cart")

def wishlist(request):
    ids = request.session.get("wishlist", [])
    return render(request, "store/wishlist.html", {"products": Product.objects.filter(id__in=ids)})

def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id); ids = request.session.get("wishlist", [])
    if product_id in ids: ids.remove(product_id); event = "wishlist_remove"
    else: ids.append(product_id); event = "wishlist_add"
    request.session["wishlist"] = ids; track(request, event, product)
    return redirect(request.POST.get("next", "wishlist"))

def enquiry(request):
    product = Product.objects.filter(id=request.GET.get("product")).first() if request.GET.get("product") else None
    form = EnquiryForm(request.POST or None, initial={"subject": f"Enquiry about {product.name}" if product else "Showroom enquiry"})
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False); record.reference = f"SF-{date.today().year}-{uuid4().hex[:6].upper()}"; record.product = product; record.user = request.user if request.user.is_authenticated else None; record.save()
        track(request, "product_enquiry_submitted" if product else "showroom_request_submitted", product, {"reference": record.reference})
        return render(request, "store/success.html", {"reference": record.reference})
    if request.method == "GET": track(request, "product_enquiry_started" if product else "showroom_request_started", product)
    return render(request, "store/enquiry.html", {"form": form, "product": product})

def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False); record.reference = f"SF-{date.today().year}-{uuid4().hex[:6].upper()}"; record.user = request.user if request.user.is_authenticated else None; record.save(); track(request, "contact_form_submitted"); messages.success(request, "Thank you. Our showroom team will be in touch."); return redirect("contact")
    return render(request, "store/contact.html", {"form": form})

def showroom(request): return render(request, "store/showroom.html")
def about(request): return render(request, "store/about.html")
def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        from django.contrib.auth import login
        login(request, user)
        track(request, "registration")
        return redirect("account")
    return render(request, "registration/register.html", {"form": form})
@login_required
def account(request): return render(request, "store/account.html", {"enquiries": Enquiry.objects.filter(user=request.user).order_by("-created_at")})

def analytics(request):
    events = AnalyticsEvent.objects.all(); top_products = Product.objects.filter(analyticsevent__name="product_view").annotate(views=Count("analyticsevent")).order_by("-views")[:8]
    return render(request, "store/analytics.html", {"events": events, "top_products": top_products, "event_counts": events.values("name").annotate(total=Count("id")).order_by("-total")[:10]})

def analytics_event(request):
    if request.method != "POST": return JsonResponse({"detail": "POST required"}, status=405)
    try: payload = json.loads(request.body or "{}")
    except json.JSONDecodeError: return JsonResponse({"detail": "Invalid JSON"}, status=400)
    product = Product.objects.filter(pk=payload.get("productId")).first()
    track(request, payload.get("event", "custom_event"), product, payload)
    return JsonResponse({"ok": True})

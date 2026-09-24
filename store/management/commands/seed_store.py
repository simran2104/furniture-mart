from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from store.models import Category, Product

CATEGORIES = {
    "Living Room": ["Sofas", "Recliners", "Coffee Tables", "TV Units", "Bookshelves", "Display Cabinets"],
    "Bedroom": ["Beds", "Wardrobes", "Bedside Tables", "Dressing Tables", "Chest of Drawers", "Mirrors"],
    "Kitchen": ["Kitchen Cabinets", "Tall Units", "Kitchen Islands", "Pantry Units", "Storage Units"],
    "Dining Room": ["Dining Tables", "Dining Chairs", "Dining Sets", "Crockery Units", "Sideboards"],
    "Study Room": ["Study Tables", "Office Chairs", "Computer Tables", "Bookshelves", "Study Cabinets"],
    "Office": ["Office Desks", "Executive Tables", "Workstations", "Office Chairs", "Filing Cabinets"],
    "Outdoor": ["Garden Chairs", "Outdoor Tables", "Benches", "Balcony Furniture", "Patio Sets"],
    "Storage": ["Cabinets", "Shoe Racks", "Bookshelves", "Storage Units", "Drawers"],
    "Home Furnishing": ["Lamps", "Cushions", "Rugs", "Wall Shelves", "Decorative Furniture"],
}
PREFIXES = ["Heritage", "Urban", "Royal", "Sundar", "Classic", "Studio", "Mosaic", "Haven", "Crafted", "Nava"]
MATERIALS = ["Sheesham Wood", "Teak Wood", "Mango Wood", "Engineered Wood", "MDF", "Plywood", "Metal", "Fabric"]
COLOURS = ["Natural Walnut", "Honey Oak", "Warm Teak", "Charcoal", "Ivory", "Forest Green", "Terracotta"]
PEXELS_BASE = "https://images.pexels.com/photos/{}/pexels-photo-{}.jpeg?auto=compress&cs=tinysrgb&w=1200"
PEXELS_IMAGES = {
    "Living Room": [7166647, 1743226, 7166931, 7546231, 7546718, 7166929, 6580372, 7001068],
    "Bedroom": [271743, 1648768, 1457842, 262048, 206064],
    "Kitchen": [1080721, 1599791, 280222, 2062426, 7546715],
    "Dining Room": [8082211, 7546715, 7546707, 2029663, 1599791],
    "Study Room": [667838, 209151, 3768126, 374074, 3769021],
    "Office": [3184436, 3760067, 380769, 1957477, 3184465],
    "Outdoor": [157811, 1287124, 1268855, 1458694, 1248583],
    "Storage": [1571460, 279648, 1148955, 1090638, 1662135],
    "Home Furnishing": [1457847, 1648771, 157811, 7546213, 1662135],
}
MATERIAL_FINISHES = ["Hand-finished protective lacquer", "Natural oil and wax finish", "Matte water-based finish", "Brushed woodgrain finish"]
STYLES = ["contemporary", "heritage-inspired", "minimalist", "transitional"]

class Command(BaseCommand):
    help = "Create the Sarvotam catalogue and a development admin user."
    def handle(self, *args, **options):
        categories = []
        for name, children in CATEGORIES.items():
            parent, _ = Category.objects.get_or_create(slug=slugify(name), defaults={"name": name})
            categories.append(parent)
            for child in children: Category.objects.get_or_create(slug=slugify(f"{name}-{child}"), defaults={"name": child, "parent": parent})
        Product.objects.all().delete()
        leaf_categories = list(Category.objects.filter(parent__isnull=False))
        for index in range(900):
            category = leaf_categories[index % len(leaf_categories)]
            room = category.parent.name
            product_type = category.name.rstrip("s")
            style = STYLES[index % len(STYLES)]
            material = MATERIALS[index % len(MATERIALS)]
            name = f"{PREFIXES[index % len(PREFIXES)]} {style.title()} {product_type}"
            price = Decimal(1800 + ((index * 137) % 118000))
            image_ids = PEXELS_IMAGES[room]
            gallery = [PEXELS_BASE.format(photo_id, photo_id) for photo_id in [image_ids[(index + offset) % len(image_ids)] for offset in range(4)]]
            Product.objects.create(sku=f"SF-{index + 1:05d}", name=name, slug=slugify(f"{name}-{index + 1}"), description=f"A {style} {product_type.lower()} made for Indian homes, with the character of {material.lower()} and proportions suited to everyday use. Visit Sarvotam Furniture in Yamunanagar to experience the finish and comfort in person.", short_description=f"A considered {product_type.lower()} for your {room.lower()}.", category=category, material=material, colour=COLOURS[index % len(COLOURS)], finish=MATERIAL_FINISHES[index % len(MATERIAL_FINISHES)], dimensions=f"{80 + index % 140} W x {45 + index % 70} D x {55 + index % 120} H cm", weight=Decimal(8 + index % 52), price=price, discount_price=price - Decimal((index % 6) * 500) if index % 3 == 0 else None, image_url=gallery[0], image_urls=gallery, rating=Decimal("4.2") + Decimal(index % 8) / 10, review_count=12 + index % 180, stock_quantity=3 + index % 20, featured=index < 16, new_arrival=index >= 800, popular=index % 5 == 0, customizable=index % 4 == 0)
        User.objects.get_or_create(username="demo-admin", defaults={"email": "admin@example.local", "is_staff": True, "is_superuser": True})
        user = User.objects.get(username="demo-admin"); user.set_password("SarvotamDemo2026!"); user.is_staff = user.is_superuser = True; user.save()
        self.stdout.write(self.style.SUCCESS(f"Seeded {Product.objects.count()} products across {Category.objects.count()} categories. Admin: demo-admin / SarvotamDemo2026!"))

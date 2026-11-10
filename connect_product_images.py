
import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.conf import settings
from store.models import Product

image_folder = (
    Path(settings.BASE_DIR)
    / "store"
    / "static"
    / "store"
    / "images"
)

image_names = {
    "Wireless Headphones": "wireless-headphones",
    "Bluetooth Speaker": "bluetooth-speaker",
    "Smart Watch": "smart-watch",
    "Wireless Mouse": "wireless-mouse",
    "Casual Sneakers": "casual-sneakers",
    "Classic Backpack": "classic-backpack",
    "Cotton T-Shirt": "cotton-t-shirt",
    "Wrist Watch": "wrist-watch",
    "Table Lamp": "table-lamp",
    "Water Bottle": "water-bottle",
    "Cookware Set": "cookware-set",
    "Storage Containers": "storage-containers",
    "Building Blocks": "building-blocks",
    "Board Game": "board-game",
    "Remote Control Car": "remote-control-car",
    "Yoga Mat": "yoga-mat",
    "Garden Tool Set": "garden-tool-set",
    "Outdoor Lantern": "outdoor-lantern",
    "Python Programming": "python-programming",
    "Study Planner": "study-planner",
    "Mystery Novel": "mystery-novel",
    "Organic Rice": "organic-rice",
    "Mixed Nuts": "mixed-nuts",
    "Green Tea": "green-tea",
    "Face Moisturizer": "face-moisturizer",
    "Shampoo": "shampoo",
    "Sunscreen": "sunscreen",
    "Dumbbell Set": "dumbbell-set",
    "Skipping Rope": "skipping-rope",
    "Sports Water Bottle": "sports-water-bottle",
    "Phone Stand": "phone-stand",
    "Laptop Sleeve": "laptop-sleeve",
    "Desk Organizer": "desk-organizer",
}

extensions = [".jpg", ".jpeg", ".png", ".webp"]

connected = 0

for product in Product.objects.all():
    base_name = image_names.get(product.name)

    if not base_name:
        print(f"Product not listed: {product.name}")
        continue

    image_file = next(
        (
            image_folder / (base_name + ext)
            for ext in extensions
            if (image_folder / (base_name + ext)).is_file()
        ),
        None,
    )

    if image_file is None:
        print(f"Image not found: {base_name}")
        continue

    product.image_url = (
        f"/static/store/images/{image_file.name}"
    )
    product.save(update_fields=["image_url"])

    connected += 1
    print(f"Connected: {product.name} -> {image_file.name}")

print(f"\nFinished! Connected {connected} product images.")


import os
import csv
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.conf import settings
from store.models import Product

IMAGE_FOLDER = os.path.join(
    settings.BASE_DIR,
    "store",
    "static",
    "store",
    "images",
)

os.makedirs(IMAGE_FOLDER, exist_ok=True)

API_URL = "https://api.openverse.org/v1/images/"

session = requests.Session()
session.headers.update({
    "User-Agent": "ShopEaseStudentProject/1.0"
})

records = []

for product in Product.objects.all():
    print(f"\nSearching: {product.name}")

    try:
        search_response = session.get(
            API_URL,
            params={
                "q": product.name,
                "page_size": 5,
                "license_type": "all-cc",
                "mature": "false",
            },
            timeout=30,
        )
        search_response.raise_for_status()
        results = search_response.json().get("results", [])

    except (requests.RequestException, ValueError) as error:
        print(f"Search failed: {error}")
        continue

    downloaded = False

    for result in results:
        image_url = result.get("url")

        if not image_url:
            continue

        try:
            response = session.get(
                image_url,
                timeout=30,
            )
            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).split(";")[0].lower()

            extensions = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/webp": ".webp",
                "image/gif": ".gif",
            }

            extension = extensions.get(content_type)

            if not extension:
                continue

            data = response.content

            valid_image = (
                data.startswith(b"\xff\xd8\xff")
                if extension == ".jpg"
                else data.startswith(b"\x89PNG\r\n\x1a\n")
                if extension == ".png"
                else data.startswith(b"RIFF")
                and data[8:12] == b"WEBP"
                if extension == ".webp"
                else data.startswith((b"GIF87a", b"GIF89a"))
            )

            if not valid_image or len(data) < 1000:
                continue

            filename = f"product_{product.id}{extension}"
            filepath = os.path.join(IMAGE_FOLDER, filename)

            with open(filepath, "wb") as image_file:
                image_file.write(data)

            product.image_url = (
                f"/static/store/images/{filename}"
            )
            product.save(update_fields=["image_url"])

            records.append({
                "product": product.name,
                "image_file": filename,
                "image_title": result.get("title", ""),
                "creator": result.get("creator", ""),
                "license": result.get("license", ""),
                "source_page": result.get("foreign_landing_url", ""),
                "license_url": result.get("license_url", ""),
            })

            print(f"DOWNLOADED: {product.name} -> {filename}")
            downloaded = True
            break

        except requests.RequestException as error:
            print(f"Image download failed: {error}")

    if not downloaded:
        print(f"NO IMAGE FOUND: {product.name}")

    # Avoid sending too many requests too quickly.
    import time
    time.sleep(1)

if records:
    csv_path = os.path.join(IMAGE_FOLDER, "image_credits.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

print("\nFinished searching for product images.")
print(f"Image folder: {IMAGE_FOLDER}")

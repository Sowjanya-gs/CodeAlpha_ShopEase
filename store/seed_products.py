
from store.models import Product

products = [
    # Electronics
    ("Wireless Headphones", "Electronics", "Comfortable wireless headphones with clear sound.", 1499, 10),
    ("Bluetooth Speaker", "Electronics", "Portable speaker for music at home or outdoors.", 999, 15),
    ("Smart Watch", "Electronics", "Smart watch for everyday activities and notifications.", 2499, 12),
    ("Wireless Mouse", "Electronics", "Ergonomic wireless mouse for work and study.", 499, 20),

    # Fashion
    ("Casual Sneakers", "Fashion", "Everyday sneakers with a comfortable fit.", 1299, 15),
    ("Classic Backpack", "Fashion", "Spacious backpack for college and travel.", 899, 18),
    ("Cotton T-Shirt", "Fashion", "Soft cotton T-shirt for daily wear.", 399, 25),
    ("Wrist Watch", "Fashion", "Classic wrist watch with a simple design.", 1199, 10),

    # Home & Kitchen
    ("Table Lamp", "Home & Kitchen", "Modern lamp for your study table or bedroom.", 899, 12),
    ("Water Bottle", "Home & Kitchen", "Reusable water bottle for everyday use.", 299, 30),
    ("Cookware Set", "Home & Kitchen", "Useful cookware set for everyday cooking.", 1799, 8),
    ("Storage Containers", "Home & Kitchen", "Containers to organize kitchen essentials.", 499, 20),

    # Toys & Games
    ("Building Blocks", "Toys & Games", "Colorful building blocks for creative play.", 699, 12),
    ("Board Game", "Toys & Games", "A fun board game for family game nights.", 549, 10),
    ("Remote Control Car", "Toys & Games", "Remote control car for indoor and outdoor play.", 999, 9),

    # Home & Outdoors
    ("Yoga Mat", "Home & Outdoors", "Comfortable mat for yoga and stretching.", 699, 15),
    ("Garden Tool Set", "Home & Outdoors", "Basic tools for home gardening.", 799, 8),
    ("Outdoor Lantern", "Home & Outdoors", "Portable lantern for outdoor activities.", 599, 12),

    # Books
    ("Python Programming", "Books", "Beginner-friendly introduction to Python programming.", 499, 20),
    ("Study Planner", "Books", "Planner for organizing study schedules and tasks.", 199, 30),
    ("Mystery Novel", "Books", "A mystery novel for your reading collection.", 349, 14),

    # Groceries
    ("Organic Rice", "Groceries", "Everyday rice for home cooking.", 199, 25),
    ("Mixed Nuts", "Groceries", "A snack mix of assorted nuts.", 299, 18),
    ("Green Tea", "Groceries", "Green tea for a refreshing hot drink.", 249, 20),

    # Beauty & Personal Care
    ("Face Moisturizer", "Beauty", "Daily moisturizer for your skincare routine.", 499, 16),
    ("Shampoo", "Beauty", "Everyday shampoo for hair care.", 299, 20),
    ("Sunscreen", "Beauty", "Sunscreen for daily sun protection.", 399, 18),

    # Sports & Fitness
    ("Dumbbell Set", "Sports", "Dumbbells for home strength workouts.", 1499, 8),
    ("Skipping Rope", "Sports", "Skipping rope for cardio exercise.", 199, 25),
    ("Sports Water Bottle", "Sports", "Reusable bottle for workouts and sports.", 349, 20),

    # More Categories
    ("Phone Stand", "Other", "Desk stand for holding a smartphone.", 249, 20),
    ("Laptop Sleeve", "Other", "Protective sleeve for carrying a laptop.", 599, 12),
    ("Desk Organizer", "Other", "Organizer for pens, stationery and desk items.", 399, 15),
]

created_count = 0

created_count = 0
updated_count = 0

# Product-specific image search keywords.
# These URLs request images matching each product.
image_keywords = {
    "Wireless Headphones": "wireless,headphones",
    "Bluetooth Speaker": "bluetooth,speaker",
    "Smart Watch": "smartwatch",
    "Wireless Mouse": "computer,mouse",
    "Casual Sneakers": "casual,sneakers",
    "Classic Backpack": "backpack",
    "Cotton T-Shirt": "cotton,tshirt",
    "Wrist Watch": "wristwatch",
    "Table Lamp": "table,lamp",
    "Water Bottle": "water,bottle",
    "Cookware Set": "cookware",
    "Storage Containers": "food,storage,containers",
    "Building Blocks": "building,blocks,toy",
    "Board Game": "board,game",
    "Remote Control Car": "toy,car",
    "Yoga Mat": "yoga,mat",
    "Garden Tool Set": "garden,tools",
    "Outdoor Lantern": "outdoor,lantern",
    "Python Programming": "python,programming,book",
    "Study Planner": "study,planner",
    "Mystery Novel": "mystery,novel,book",
    "Organic Rice": "rice,grains",
    "Mixed Nuts": "mixed,nuts",
    "Green Tea": "green,tea",
    "Face Moisturizer": "face,moisturizer",
    "Shampoo": "shampoo,bottle",
    "Sunscreen": "sunscreen",
    "Dumbbell Set": "dumbbells,fitness",
    "Skipping Rope": "skipping,rope",
    "Sports Water Bottle": "sports,water,bottle",
    "Phone Stand": "phone,stand",
    "Laptop Sleeve": "laptop,sleeve",
    "Desk Organizer": "desk,organizer",
}

for name, category, description, price, stock in products:
    keywords = image_keywords.get(name, "product")
    image_url = f"https://loremflickr.com/600/600/{keywords}"

    product, created = Product.objects.get_or_create(
        name=name,
        defaults={
            "category": category,
            "description": description,
            "price": price,
            "stock": stock,
            "image_url": image_url,
        },
    )

    if created:
        created_count += 1
    else:
        changed_fields = []

        if product.category != category:
            product.category = category
            changed_fields.append("category")

        if product.image_url != image_url:
            product.image_url = image_url
            changed_fields.append("image_url")

        if changed_fields:
            product.save(update_fields=changed_fields)
            updated_count += 1

print("Product image setup completed!")
print("New products added:", created_count)
print("Existing products updated:", updated_count)
print("Total products:", Product.objects.count())
print(
    "Products with image URLs:",
    Product.objects.exclude(image_url="").count()
)

updated_count = 0

for name, category, description, price, stock in products:
    product, created = Product.objects.get_or_create(
        name=name,
        defaults={
            "category": category,
            "description": description,
            "price": price,
            "stock": stock,
        },
    )

    if created:
        created_count += 1
    else:
        if product.category != category:
            product.category = category
            product.save(update_fields=["category"])
            updated_count += 1

print("Product setup completed!")
print("New products added:", created_count)
print("Existing products recategorized:", updated_count)
print("Total products in database:", Product.objects.count())

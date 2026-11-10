# ShopEase - Discover More. Shop Smarter.

ShopEase is a Django-based e-commerce web application developed as part of the CodeAlpha Full Stack Development Internship.

The platform allows users to browse products, view product details, manage shopping carts, place orders, save delivery addresses, and submit product reviews.

## Features

- Product listing and product details
- Product categories and search
- Shopping cart with quantity and stock validation
- Buy Now functionality
- User registration and login
- Product ratings and customer reviews
- Checkout and order placement
- Cash on Delivery and demo UPI payment options
- Saved delivery addresses
- Order history
- Stock management after successful orders

## Technologies Used

- Python
- Django
- HTML5
- CSS3
- JavaScript
- SQLite
- Browser Local Storage and Session Storage

## Installation and Setup

### 1. Download the project

Clone or download this repository and open the project folder in PowerShell.

### 2. Install Django

```powershell
python -m pip install Django==6.1.2
```

### 3. Configure the Django secret key

Generate a secret key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set the generated key in PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "PASTE_YOUR_GENERATED_KEY_HERE"
```

### 4. Apply database migrations

```powershell
python manage.py migrate
```

### 5. Start the development server

```powershell
python manage.py runserver
```

### 6. Open the application

Visit:

http://127.0.0.1:8000/

## Project Structure

- `config/` - Django project configuration
- `store/` - E-commerce application
- `store/templates/store/` - HTML templates
- `store/static/store/` - CSS, JavaScript, and product images
- `store/migrations/` - Database migrations
- `manage.py` - Django management utility

## Security Notes

- Keep secret keys and environment variables private.
- Do not upload your database, personal data, or backup files to a public repository.
- This project uses demo payment options and does not process real payments.

## Developer

Developed as a full-stack e-commerce project for the CodeAlpha Internship.
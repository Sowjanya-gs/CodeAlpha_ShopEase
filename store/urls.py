
from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path("", views.product_list, name="product_list"),

    # Products
    path(
        "product/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),
    path(
    "product/<int:product_id>/review/",
    views.submit_review,
    name="submit_review"
),

    # Cart and checkout
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("place-order/", views.place_order, name="place_order"),

    # Account and authentication
    path("account/", views.account, name="account"),
    path("login/", views.login_signup, name="login_signup"),
    path("logout/", views.logout_user, name="logout"),

    # Wishlist
    path("wishlist/", views.wishlist, name="wishlist"),

    # Saved addresses
    path("addresses/", views.addresses, name="addresses"),
    path("addresses/add/", views.add_address, name="add_address"),
    path(
    "addresses/save-checkout/",
    views.save_checkout_address,
    name="save_checkout_address"
),
    path(
        "addresses/<int:address_id>/edit/",
        views.edit_address,
        name="edit_address"
    ),
    path(
        "addresses/<int:address_id>/delete/",
        views.delete_address,
        name="delete_address"
    ),
    path(
        "addresses/<int:address_id>/default/",
        views.set_default_address,
        name="set_default_address"
    ),

    # Order history
    path("my-orders/", views.my_orders, name="my_orders"),
]

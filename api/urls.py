from django.urls import path, include
from . import views
from rest_framework_nested import routers


# the below code is for nested routers in modelviewset
router = routers.DefaultRouter()

router.register("products", views.ProductViewset)
router.register("categories", views.CategoryViewset)
router.register("carts", views.CartViewset)
# router.register("profile", views.ProfileViewset)
router.register("orders", views.OrderViewset, basename="orders")
router.register("subscription", views.SubscriptionViewset)

products_router = routers.NestedDefaultRouter(router, "products", lookup="product") # In DRF, nested router automatically appends _pk to the lookup field, to prevent naming conflicts and to follow a common naming convention. (product_pk)
products_router.register("reviews", views.ReviewViewset, basename="product-reviews") # here, basename is optional

cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewset, basename="cart-items")


urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(cart_router.urls)),
    path('emailsend/', views.send_mail_to_users)
]



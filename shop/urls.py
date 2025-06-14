"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
"""
from django.urls import path
from .views import index, signup, login, productdetail, products, cartoperations, buynow, checkout, logout, cart, account
from .views import wishlist, search, updateprofile, changepassword, postreview, contact, about, cancelproduct, payment, policy, branches, terms
from . import views
from shop.views.passwordreset import password_reset, reset

urlpatterns = [
    path("", index.index, name="ShopHome"),
    path("signup/", signup.Signup.as_view(), name="SignUp"),
    path("login/", login.Login.as_view(), name="LogIn"),
    path("products/", products.products, name="Products"),
    path("search/", search.search, name="Search"),
    path("productdetail/<int:prid>", productdetail.productdetail, name="ProductDetail"),
    path('fetch_related_products/<int:product_id>/', productdetail.fetch_related_products, name='fetch_related_products'),
    path("addtocart/<int:prid>", cartoperations.addtocart, name="AddtoCart"),
    path("buynow/<int:prid>", buynow.buynow, name="BuyNow"),
    path("postreview/<int:prid>", postreview.postreview, name="PostReview"),
    path("deletefromcart/<int:prid>", cartoperations.deletefromcart, name="DeletefromCart"),
    path("deleteallfromcart/<int:prid>", cartoperations.deleteallfromcart, name="DeleteAllfromCart"),
    path("addtowishlist/<int:prid>", wishlist.addtowishlist, name="AddfromWishlist"),
    path("removefromwishlist/<int:prid>", wishlist.removefromwishlist, name="RemovefromWishlist"),
    path("cart/", cart.cart, name="Cart"),
    path("clearcart/", cartoperations.clearcart, name="ClearCart"),
    path("checkout/", checkout.checkout, name="CheckOut"),
    path("cancelproduct/<int:orid>/<int:prid>", cancelproduct.cancelProduct, name="CancelProduct"),
    path("contactus/", contact.contact, name="ContactUs"),
    path("about/", about.about, name="AboutUs"),
    path("account/", account.account, name="Account"),
    path("account/updateprofile/", updateprofile.updateprofile, name="UpdateProfile"),
    path("account/changepassword/", changepassword.changepassword, name="ChangePassword"),
    path("logout/", logout.logout_view, name="Logout"),
    path('activate/<str:uidb64>/<str:token>/', signup.Signup.activate, name='activate'),
    path('forgot_password/', password_reset, name = 'forgot_password'),
    path('reset/<str:uidb64>/<str:token>/', reset, name = 'reset'),
    path('mpesa-checkout/', payment.MpesaCheckout.as_view(), name='mpesa_checkout'),
    path('mpesa-callback/', payment.MpesaCallBack.as_view(), name='mpesa_callback'),
    path('policy/', policy.policy, name='policy'),
    path('branches/', branches.branches, name='branches'),
    path('terms/', terms.terms, name='terms'),
]

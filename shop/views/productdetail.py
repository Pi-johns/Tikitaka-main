from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from shop.models import Customer, Product, Review, Cart, Wishlist, Category
from django.http import JsonResponse
from celery import chain

def get_related_products(product):
    return Product.objects.filter(category=product.category).exclude(id=product.id)

def fetch_related_products(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    page_number = request.GET.get('page', 1)
    related_products_list = get_related_products(product)
    paginator = Paginator(related_products_list, 10)
    
    try:
        related_products = paginator.page(page_number)
    except PageNotAnInteger:
        related_products = paginator.page(1)
    except EmptyPage:
        related_products = paginator.page(paginator.num_pages)

    products = [{
        'id': related_product.id,
        'name': related_product.name,
        'price': related_product.price,
        'url': related_product.get_absolute_url(),  # Make sure you have get_absolute_url method in your Product model
        'image_url': related_product.image.url if related_product.image else ''
    } for related_product in related_products]
    
    response_data = {
        'products': products,
        'has_next': related_products.has_next(),
        'next_page_number': related_products.next_page_number() if related_products.has_next() else None,
    }

    return JsonResponse(response_data)
def productdetail(request, prid):
    current_user = request.user
    product = Product.objects.get(id=prid)
    reviews = Review.objects.filter(product_id=prid)
    carts = Cart.objects.filter(user_id=current_user.id)
    wishlist = Wishlist.objects.filter(user_id=current_user.id, product_id=prid)

    customer = []
    try:
        customer = Customer.objects.get(user_id=current_user.id)
    except:
        pass

    try:
        pr_qty = Cart.objects.get(user_id=current_user.id, product_id=prid)
        pr_qty = pr_qty.qty
    except:
        pr_qty = 0

    no_of_reviews = len(reviews)
    
    rating = 0
    for review in reviews:
        rating = rating + review.rating
    try:
        rating = rating / no_of_reviews
    except:
        pass

    desc = product.description
    descs = list(desc.split("#"))

    qty = 0
    total = 0
    for cart in carts:
        total = total + cart.amount
        qty = qty + cart.qty
        
    # Fetch related products with pagination
    related_products_list = get_related_products(product)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(related_products_list, 10)  # Show 4 related products per page
    
    try:
        related_products = paginator.page(page_number)
    except PageNotAnInteger:
        related_products = paginator.page(1)
    except EmptyPage:
        related_products = paginator.page(paginator.num_pages)
    
    details = {
        'customer': customer,
        'product': product,
        'descs': descs,
        'reviews': reviews,
        'no_of_reviews': no_of_reviews,
        'rating': rating,
        'qty': qty,
        'total': total,
        'carts': carts,
        'wishlist': wishlist,
        'pr_qty': pr_qty,
        'related_products': related_products,
        'has_next': related_products.has_next(),
        'next_page_number': related_products.next_page_number() if related_products.has_next() else None,
    }

    
    return render(request, 'productdetail.html', details)


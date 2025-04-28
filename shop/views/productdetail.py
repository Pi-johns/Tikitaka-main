from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from shop.models import Customer, Product, Review, Cart, Wishlist, Category
from django.http import JsonResponse
from django.db.models import Avg, Count
from django.utils import timezone

def get_related_products(product):
    return Product.objects.filter(category=product.category).exclude(id=product.id)

def get_bestsellers():
    return Product.objects.annotate(
        review_count=Count('review')
    ).order_by('-review_count')[:5]

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
        'name': related_product.product_name,
        'price': related_product.price,
        'url': related_product.get_absolute_url(),
        'image_url': related_product.product_img.url if related_product.product_img else ''
    } for related_product in related_products]
    
    response_data = {
        'products': products,
        'has_next': related_products.has_next(),
        'next_page_number': related_products.next_page_number() if related_products.has_next() else None,
    }

    return JsonResponse(response_data)


def productdetail(request, prid):
    current_user = request.user
    product = get_object_or_404(Product, id=prid)
    reviews = Review.objects.filter(product_id=prid).select_related('customer')
    carts = Cart.objects.filter(user_id=current_user.id) if current_user.is_authenticated else []
    
    # Review statistics
    review_stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Customer data
    customer = None
    pr_qty = 0
    wishlist = False
    
    if current_user.is_authenticated:
        try:
            customer = Customer.objects.get(user_id=current_user.id)
        except Customer.DoesNotExist:
            pass
        
        try:
            pr_qty = Cart.objects.get(user_id=current_user.id, product_id=prid).qty
        except Cart.DoesNotExist:
            pass
            
        wishlist = Wishlist.objects.filter(user_id=current_user.id, product_id=prid).exists()

    # Process description
    desc = product.description
    descs = list(desc.split("#")) if desc else []
    
    # Cart totals
    qty = 0
    total = 0
    for cart in carts:
        total = total + cart.amount
        qty = qty + cart.qty
        
    # Related products
    related_products_list = get_related_products(product)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(related_products_list, 10)
    
    try:
        related_products = paginator.page(page_number)
    except PageNotAnInteger:
        related_products = paginator.page(1)
    except EmptyPage:
        related_products = paginator.page(paginator.num_pages)
    
    # Bestsellers
    bestsellers = get_bestsellers()
    
    # Prepare specifications (assuming product.specs is a JSONField)
    specs = getattr(product, 'specs', {})
    
    details = {
        'customer': customer,
        'product': product,
        'descs': descs,
        'reviews': reviews,
        'no_of_reviews': review_stats['total_reviews'] or 0,
        'rating': review_stats['avg_rating'] or 0,
        'qty': qty,
        'total': total,
        'carts': carts,
        'wishlist': wishlist,
        'pr_qty': pr_qty,
        'related_products': related_products,
        'has_next': related_products.has_next(),
        'next_page_number': related_products.next_page_number() if related_products.has_next() else None,
        'bestsellers': bestsellers,
        'specs': specs,
    }

    return render(request, 'productdetail.html', details)
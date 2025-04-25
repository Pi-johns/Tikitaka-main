from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from shop.models import Category, Customer, Product, Cart, Review

@cache_page(60 * 15)  # Cache for 15 minutes
def products(request):
    current_user = request.user
    customer = []
    try:
        customer = Customer.objects.get(user_id=current_user.id)
    except:
        pass

    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, 3600)  # Cache for 1 hour


    categoryid = 0
    filtered_category = []

    try:
        categoryid = request.GET['category']
    except:
        pass
    cache_key = f"products_{categoryid}"
    products = cache.get(cache_key)
    if not products:
        if categoryid:
            products = Product.objects.filter(category_id=categoryid)
            try:
               filtered_category = Category.objects.get(id=categoryid)
            except Category.DoesNotExist:
               pass
        else:
            products = Product.objects.all()
        cache.set(cache_key, products, 3600)  # Cache for 1 hour
    
    products_with_ratings = Product.objects.filter(review__rating__isnull=False).distinct()
    products_with_ratings_info = []

    for product in products_with_ratings:
        rating_count = Review.objects.filter(product=product).exclude(rating__isnull=True).count()
        products_with_ratings_info.append({
            'product': product,
            'rating_count': rating_count or 0 
        })
        
    n = len(products)
    current_user = request.user
    carts = Cart.objects.filter(user_id=current_user.id)
    qty = 0
    total = 0
    for cart in carts:
        total = total + cart.amount
        qty = qty + cart.qty

    params = {
        'customer':customer,
        'products': products,
        'categories': categories,
        'filtered_category': filtered_category,
        'qty': qty,
        'n':n,
        'total':total,
        'carts':carts,
        'products_with_ratings_info':products_with_ratings_info,
        }
    
    return render(request, 'products.html', params)

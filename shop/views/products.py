from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db.models import Q, Avg, Count
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

    # Initialize variables
    categoryid = request.GET.get('category', 0)
    filtered_category = None
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    sort_by = request.GET.get('sort_by')
    tag_filter = request.GET.get('tag')
    rating_filter = request.GET.get('rating')
    
    # Base queryset
    products = Product.objects.all()
    
    # Apply category filter if specified
    if categoryid:
        products = products.filter(category_id=categoryid)
        try:
            filtered_category = Category.objects.get(id=categoryid)
        except Category.DoesNotExist:
            pass
    
    # Apply price range filter
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    
    # Apply tag filter
    if tag_filter:
        products = products.filter(tag=tag_filter)
    
    # Apply rating filter
    if rating_filter:
        # Get products with average rating >= selected rating
        products = products.annotate(
            avg_rating=Avg('review__rating'),
            review_count=Count('review')
        ).filter(avg_rating__gte=rating_filter, review_count__gt=0)
    
    # Apply sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.annotate(
            avg_rating=Avg('review__rating')
        ).order_by('-avg_rating')
    
    # Get unique tags for filter options
    tags = Product.objects.values_list('tag', flat=True).distinct()
    
    # Get products with ratings info for display
    products_with_ratings_info = {
    product.id: {
        'rating_count': rating_count,
        'avg_rating': avg_rating
    }
    for product in products
    for rating_count in [Review.objects.filter(product=product).count()]
    for avg_rating in [Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0]
}

    
    # Cart information
    n = products.count()
    current_user = request.user
    carts = Cart.objects.filter(user_id=current_user.id)
    qty = 0
    total = 0
    for cart in carts:
        total = total + cart.amount
        qty = qty + cart.qty

    params = {
        'customer': customer,
        'products': products,
        'categories': categories,
        'filtered_category': filtered_category,
        'qty': qty,
        'n': n,
        'total': total,
        'carts': carts,
        'products_with_ratings_info': products_with_ratings_info,
        'tags': tags,
        'selected_tag': tag_filter,
        'selected_rating': int(rating_filter) if rating_filter else None,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
    }
    
    return render(request, 'products.html', params)
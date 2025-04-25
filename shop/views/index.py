from django.views import View
from django.shortcuts import render
from shop.models import Category, Customer, Product, Cart, Review
from slides.models import Slide

def index(request):
    current_user = request.user
    categories = Category.objects.all()
    products = Product.objects.all()
    carts = Cart.objects.filter(user_id=current_user.id)
    billiards = Product.objects.filter(category_id=3)
    seconds = Product.objects.filter(category_id=4)
    slides = Slide.objects.filter(is_active=True).order_by('display_order')
    
    products_with_ratings = Product.objects.filter(review__rating__isnull=False).distinct()
    products_with_ratings_info = []

    for product in products_with_ratings:
        rating_count = Review.objects.filter(product=product).exclude(rating__isnull=True).count()
        products_with_ratings_info.append({
            'product': product,
            'rating_count': rating_count or 0 
        })
    
        
    customer = []
    try:
        customer = Customer.objects.get(user_id=current_user.id)
    except:
        pass

    qty = 0
    total = 0
    for cart in carts:
        total = total + cart.amount
        qty = qty + cart.qty

    params = {
        'customer':customer,
        'slides':slides,
        'products':products,
        'categories':categories,
        'qty':qty,
        'total':total,
        'carts':carts,
        'billiards':billiards,
        'seconds':seconds,
        'products_with_ratings_info':products_with_ratings_info,
    }

    return render(request, 'index.html', params)

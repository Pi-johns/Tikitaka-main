from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Customer, Order, OrderProduct, Cart
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

@login_required(login_url='/login')
def checkout(request):
    currentuser = request.user
    carts = Cart.objects.filter(user_id=currentuser.id)
    customer = Customer.objects.get(user_id=currentuser.id)
    myuser = User.objects.get(id=currentuser.id)

    total = 0
    qty = 0
    for cart in carts:
        total += cart.amount
        qty += cart.qty

    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        code = "OD-" + get_random_string(10).upper()
        # Ensure total is calculated and included when creating an Order
        order = Order(
            user_id=currentuser.id,
            first_name=firstname,
            last_name=lastname,
            phone=phone,
            city=city,
            state=state,
            code=code,
            total=total
        )
        order.save()

        for cart in carts:
            orderpr = OrderProduct(
                order_id=order.id,
                user_id=currentuser.id,
                product_id=cart.product_id,
                qty=cart.qty,
                price=cart.product.price,
                amount=cart.amount
            )
            orderpr.save()

        Cart.objects.filter(user_id=currentuser.id).delete()
        messages.success(request, "Order has been placed. Thank You 😊")
        return redirect('/mpesa-checkout')

    details = {
        'myuser': myuser,
        'customer': customer,
        'carts': carts,
        'qty': qty,
        'total': total,
    }

    return render(request, 'checkout.html', details)


import logging
import json
import math
from django.urls import reverse_lazy
from django.views import View
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from shop.payments.forms import MpesaCheckoutForm
from shop.payments.utils import MpesaGateWay
from shop.models import Order, Transaction, Cart, OrderProduct
from django.contrib.auth.models import User

gateway = MpesaGateWay()
logger = logging.getLogger("default")  # or another logger name you prefer

@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MpesaCheckout(FormView):
    template_name = 'mpesa_checkout.html'
    form_class = MpesaCheckoutForm
    success_url = reverse_lazy('payment_success')  # Define a success URL

    def get_initial(self):
        initial = super().get_initial()
        currentuser = self.request.user
        orders = Order.objects.filter(user_id=currentuser.id).order_by("-placed_at")
        if orders.exists():
            order = orders.first()
            initial['order'] = order
            self.request.session['order_id'] = order.id
        return initial

    def form_valid(self, form):
        currentuser = self.request.user
        orders = Order.objects.filter(user_id=currentuser.id).order_by("-placed_at")

        if not orders.exists():
            return JsonResponse({'error': 'No orders found.'}, status=400)

        order = orders.first()
        phone_number = form.cleaned_data['phone_number']
        
        payload = {
            "request": self.request,
            "data": { 
                "amount": int(math.ceil(float(order.total))),
                "phone_number": phone_number,
                "reference": order.code,
                "description": f"Payment for Order {order.code}"
            }
        }
        logger.debug("Payload before sending to M-PESA for Order %s: %s", order.id, payload)

        response = gateway.stk_push_request(payload)
        if 'status' not in response:
            logger.info("Response from stk_push_request: {}".format(response))
            return JsonResponse({"error": "Invalid response from payment gateway"}, status=500)
            
        if response['status'] == 0:
            Transaction.objects.create(
                order=order,
                user=self.request.user,
                phone_number=phone_number,
                checkout_request_id=response['checkout_request_id'],
                reference=order.code,
                description=f"Payment for Order {order.code}",
                amount= int(math.ceil(float(order.total))),
                status=1,  # Assuming 1 is for 'Pending'
                receipt_no=response.get('receipt_no', ''),
                ip=self.request.META.get('REMOTE_ADDR')
            )
            return JsonResponse({'message': 'Payment initiated successfully'}, status=200)
        else:
            return JsonResponse({'message': 'Payment initiation failed'}, status=400)


class MpesaCallBack(View):
    def post(self, request):
        try:
            # Log the callback data for debugging purposes
            logger.info("Callback data from M-PESA: %s", request.body.decode('utf-8'))

            # Parse the callback JSON data
            data = json.loads(request.body)

            # Extract relevant data from the callback
            checkout_request_id = data.get('CheckoutRequestID')
            result_code = data.get('ResultCode')
            result_desc = data.get('ResultDesc')
            transaction_id = data.get('TransactionID')

            # Retrieve the transaction based on CheckoutRequestID
            transaction = Transaction.objects.get(checkout_request_id=checkout_request_id)

            # Update transaction status based on M-PESA result code
            if result_code == '0':  # Successful transaction
                transaction.status = Transaction.SUCCESS  # Assuming you have a SUCCESS status in Transaction model
                transaction.receipt_no = data.get('ReceiptNo', '')
            else:
                transaction.status = Transaction.FAILED  # Assuming you have a FAILED status in Transaction model

            # Save the updated transaction
            transaction.save()

            # Respond with a success message to M-PESA
            return JsonResponse({'ResultCode': '0', 'ResultDesc': 'Success'}, status=200)

        except Transaction.DoesNotExist:
            logger.error("Transaction not found for CheckoutRequestID: %s", checkout_request_id)
            return JsonResponse({'ResultCode': '1', 'ResultDesc': 'Transaction not found'}, status=404)

        except Exception as e:
            logger.error("Error processing M-PESA callback: %s", str(e))
            return JsonResponse({'ResultCode': '1', 'ResultDesc': 'Error processing callback'}, status=500)


import logging
import time
import math
import base64
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
from django.conf import settings
from phonenumber_field.phonenumber import PhoneNumber
from shop.models import Transaction
from shop.payments.forms import TransactionForm
from django_daraja.mpesa.core import MpesaClient

logger = logging.getLogger("default")
cl = MpesaClient()
callback_url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'

class MpesaGateWay:
    def __init__(self):
        now = datetime.now()
        self.mpesa_shortcode = settings.MPESA_SHORTCODE
        self.mpesa_consumer_key = settings.MPESA_CONSUMER_KEY
        self.mpesa_consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.access_token_url = settings.ACCESS_TOKEN_URL
        self.password = self.generate_password()
        self.checkout_url = settings.CHECKOUT_URL
        self.access_token_expiration = None
        self.mpesa_passkey = settings.MPESA_PASSKEY
        self.mpesa_express_shortcode = settings.MPESA_EXPRESS_SHORTCODE
        self.access_token = None
        self.timestamp = None

        try:
            self.access_token = self.get_access_token()
            if self.access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            logger.error("Error: {}".format(e))
        else:
            self.access_token_expiration = time.time() + 3400

    def get_access_token(self):
        try:
            res = requests.get(
                self.access_token_url,
                auth=HTTPBasicAuth(self.mpesa_consumer_key, self.mpesa_consumer_secret),
            )
        except Exception as err:
            logger.error("Error: {}".format(err))
            raise err
        else:
            token = res.json()["access_token"]
            self.headers = {"Authorization": "Bearer %s" % token}
            return token

    class Decorators:
        @staticmethod
        def refresh_token(decorated):
            def wrapper(gateway, *args, **kwargs):
                if (
                    gateway.access_token_expiration
                    and time.time() > gateway.access_token_expiration
                ):
                    token = gateway.get_access_token()
                    gateway.access_token = token
                return decorated(gateway, *args, **kwargs)

            return wrapper

    def generate_password(self):
        """Generates mpesa api password using the provided shortcode and passkey"""
        now = datetime.now()
        self.timestamp = now.strftime("%Y%m%d%H%M%S")
        password_str = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + self.timestamp
        password_bytes = password_str.encode("ascii")
        return base64.b64encode(password_bytes).decode("utf-8")

    @Decorators.refresh_token
    def stk_push_request(self, payload):
        request = payload.get("request")
        data = payload.get("data") 
        amount = int(math.ceil(data["amount"]))
        transaction_desc = data.get("description")
        phone_number = data.get("phone_number")
        now = datetime.now()
        self.timestamp = now.strftime("%Y%m%d%H%M%S")
        data["amount"] = int(math.ceil(float(data["amount"])))
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        req_data = {
            "BusinessShortCode": self.mpesa_shortcode,
            "Password": self.mpesa_passkey,
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.mpesa_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://9305-41-90-184-25.ngrok-free.app/mpesa_callback",
            "AccountReference": "Kangkeyinvestment",
            "TransactionDesc": transaction_desc, 
        }
        logger.debug("Data being sent to M-PESA: %s", req_data)

        try:
            res =  requests.post(self.checkout_url, headers = headers, json = req_data)
            res.raise_for_status()
            try:
                res_data = res.json()
                logger.info("Mpesa response info: %s", res_data)
                if 'CheckoutRequestID' not in res_data:
                    raise ValueError("Missing CheckoutRequestID in response")

                data["ip"] = request.META.get("REMOTE_ADDR")
                data["checkout_request_id"] = res_data["CheckoutRequestID"]

                form = TransactionForm(data)
                if form.is_valid():
                    form.save()
                else:
                    logger.error("Transaction form errors: %s", form.errors)
                
                return res_data
            except requests.exceptions.JSONDecodeError:
                logger.error("Failed to decode JSON response: %s", res.text)
                return {"status": "error", "message": "Invalid JSON response from M-PESA"}
        except requests.exceptions.RequestException as e:
            logger.error("Request to M-PESA failed: %s", str(e))
            return {"status": "error", "message": "Request to M-PESA failed"}
 
    def check_status(self, data):
        try:
            status = data["Body"]["stkCallback"]["CheckoutRequestID"]
        except Exception as e:
            logger.error(f"Error: {e}")
            status = 2
        return status

    def get_transaction_object(self, data):
        checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
        transaction, _ = Transaction.objects.get_or_create(
            checkout_request_id=checkout_request_id
        )
        return transaction

    def handle_successful_pay(self, data, transaction):
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        for item in items:
            if item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "MpesaReceiptNumber":
                receipt_no = item["Value"]
            elif item["Name"] == "PhoneNumber":
                phone_number = item["Value"]

        transaction.amount = amount
        transaction.phone_number = PhoneNumber(raw_input=phone_number)
        transaction.receipt_no = receipt_no
        transaction.confirmed = True

        return transaction

    def callback_handler(self, data):
        status = self.check_status(data)
        transaction = self.get_transaction_object(data)
        if status == 0:
            self.handle_successful_pay(data, transaction)
        else:
            transaction.status = 1

        transaction.status = status
        transaction.save()

        transaction_data = {
            "id": transaction.id,
            "amount": transaction.amount,
            "phone_number": transaction.phone_number,
            "receipt_no": transaction.receipt_no,
            "status": transaction.status,
            "confirmed": transaction.confirmed,
        }

        logger.info("Transaction completed info: {}".format(transaction_data))

        return JsonResponse({"status": "ok", "code": 0})


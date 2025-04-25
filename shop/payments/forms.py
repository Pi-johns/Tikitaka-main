from django import forms
from django.core.exceptions import ValidationError
from .validators import validate_possible_number
from shop.models import Transaction
import logging

logger = logging.getLogger(__name__)

class MpesaCheckoutForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=13)

    class Meta:
        model = Transaction
        fields = ['phone_number']  # Specify only the fields you want to use in the form

    def validate_phone_number(self, phone_number):      
        try:
            validate_possible_number(phone_number)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise forms.ValidationError(str(e))

        return phone_number  
    def validate_amount(self, amount):
        """this methods validates the amount"""
        if not amount or float(amount) <= 0:
            raise serializers.ValidationError(
                {"error": "Amount must be greater than Zero"}
            )
        return amount

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = "__all__"


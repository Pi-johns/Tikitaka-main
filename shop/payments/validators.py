import re
from enum import Enum
from django.core.exceptions import ValidationError
from phonenumbers import is_possible_number, parse
from .error_codes import PaymentErrorCode
from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import NumberParseException

class PhoneValidationError(Enum):
    INVALID = 'invalid'
    
def validate_possible_number(phone, country):
    try:
        phone_number = parse(phone, country)
        if not is_possible_number(phone_number):
            raise ValidationError(
                "The phone number entered is not valid.", code=PaymentErrorCode.INVALID
            )
    except NumberParseException:
        raise ValidationError(
            "The phone number entered is not valid.", code=PaymentErrorCode.INVALID
        )
    return phone_number

    



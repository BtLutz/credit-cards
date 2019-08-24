from django.db import models

from baluhn import generate, verify
from logging import getLogger
from random import randint
from typing import Set

from .exceptions import InvalidCardNumberError, InvalidIinError
from .constants import CARD_LENGTH, NUMBER
LOG = getLogger(__name__)


class CreditCard(models.Model):
    """
    The Credit Card class. This class is for holding data after it is validated in CreditCard.from_number.
    """
    number = models.CharField(max_length=20, default=None)
    major_industry_identifier = models.CharField(max_length=1, default=None)
    issuer_identification_number = models.CharField(max_length=6, default=None)
    personal_account_number = models.CharField(max_length=4, default=None)
    check_digit = models.CharField(max_length=1, default=None)
    is_valid = models.BooleanField(default=False)

    @classmethod
    def from_number(cls, number: str) -> 'CreditCard':
        """
        Instantiates a CreditCard instance if *number* is numeric and pyluhn.verify returns True with it as an argument.
        Otherwise, raises an InvalidCardNumberError. For simplification, I assume that the IIN is always
        the first six digits of the number, and the PAN is the digits from the end of the IIN to the check digit.
        The check digit is always the last digit.

        :Example:
        >>> c = CreditCard.from_number("1234567890123456")
        For the number argument I found 1234567890123456, which is not a valid card number.
        Traceback (most recent call last):
          File "<console>", line 1, in <module>
          File ...
            raise InvalidCardNumberError()
        api.exceptions.InvalidCardNumberError

        :Example:
        >>> c = CreditCard.from_number("4503495455532271")
        >>> c.is_valid
        True

        :param number: "1234567890123456"
        :return: a CreditCard instance.
        """
        if not number.isdigit() or not verify(number):
            LOG.error(f"For the number argument I found {number}, which is not a valid card number.")
            raise InvalidCardNumberError()
        major_industry_identifier = number[0]  # First digit of the number is the MII
        issuer_identification_number = number[:6]  # Digits 1 -> 6 are the IIN
        personal_account_number = number[6:-1]  # The rest until the check digit are the PAN
        check_digit = number[-1]  # The check digit is the last digit in the string.
        return cls(
            number=number,
            major_industry_identifier=major_industry_identifier,
            issuer_identification_number=issuer_identification_number,
            personal_account_number=personal_account_number,
            check_digit=check_digit,
            is_valid=True
        )

    @classmethod
    def with_invalid_number(cls, number: str) -> 'CreditCard':
        """
        Instantiates a CreditCard instance with number set to *number*. All other attributes are left as default.

        :Example:
        >>> c = CreditCard.with_invalid_number("a")
        >>> c.is_valid
        False

        :param number: Any string.
        :return: a CreditCard object with is_valid set to False, and all other attributes other than number set to
        None.
        """
        return cls(number=number)

    @classmethod
    def generate_from_iin(cls, iin: str) -> 'CreditCard':
        """
        Generates a credit card instance given an iin *iin*. If *iin* is not a valid Issuer Identification number
        (For these purposes, any string of digits, without characters, of length two or one is valid),
        an InvalidIinError is thrown. You can then pipe this number back to the CreditCard.from_number function,
        and I guarantee it'll return you an object.

        :Example:
        >>> c = CreditCard.generate_from_iin("45")
        >>> c.number
        '4524504745441907'

        :param iin: r'[0-9]{1, 2}' (Any string, of only digits, of length one or two).
        :return: An initialized CreditCard object prefixed with the given IID and suffixed with the
        correct check digit.
        """
        if not (0 < len(iin) < 3) or not iin.isdigit():
            raise InvalidIinError()
        middle_digits_len = CARD_LENGTH - len(iin) - 1  # -1 for the check digit.
        middle_digits = (str(randint(0, 9)) for _ in range(middle_digits_len))
        digits_without_check_digit = iin + "".join(middle_digits)
        check_digit = generate(digits_without_check_digit)
        number = digits_without_check_digit + check_digit
        return CreditCard.from_number(number)

    def __iter__(self):
        """
        Returns an iterator over a list of tuples in the form (attribute_name, attribute_value).
        This excludes the keys I inherit from the Django Model class (_state and id) and redundant keys (number).
        :return: ("is_valid", True), ("check_digit", "6"), ...
        """
        return ((key, value) for key, value in self.__dict__.items() if key not in {"_state", "id"})

    def serialized(self, with_number: bool = False):
        """
        Serializes the CreditCard instance by casting itself to a dictionary.

        :Example:
        >>> c = CreditCard.from_number('4524504745441907')
        >>> c.serialized()
        {'major_industry_identifier': '4', 'issuer_identification_number': '452450', 'personal_account_number': '
        474544190', 'check_digit': '7', 'is_valid': True}

        :return: A dictionary representation of *self*
        """
        res = dict(self)
        if not with_number:
            del res[NUMBER]
        return res

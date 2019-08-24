from django.test import TestCase

from api.models import CreditCard
from api.exceptions import InvalidCardNumberError, InvalidIinError

from unittest.mock import patch


class CreditCardModelTests(TestCase):
    """
    Tests the CreditCard model class.
    """

    def test_from_number_with_characters(self):
        """
        Tests calling the CreditCard.from_number function with a non-numeric string argument.
        """
        self.assertRaises(InvalidCardNumberError, CreditCard.from_number, "a")

    @patch("api.models.verify")
    def test_from_number_with_invalid_number(self, mock_verify):
        """
        Tests calling the CreditCard.from_number function with a numeric argument, where pyluhn.verify returns False.
        """
        mock_verify.return_value = False
        self.assertRaises(InvalidCardNumberError, CreditCard.from_number, "1234567890123456")

    @patch("api.models.verify")
    def test_from_number_with_valid_number(self, mock_verify):
        """
        Tests calling the CreditCard.from_number function with a numeric argument, where pyluhn.verify returns True.
        """
        mock_verify.return_value = True
        res = CreditCard.from_number("1234567890123456")
        self.assertTrue(res.is_valid)
        self.assertEqual("1", res.major_industry_identifier)
        self.assertEqual("123456", res.issuer_identification_number)
        self.assertEqual("789012345", res.personal_account_number)
        self.assertEqual("6", res.check_digit)

    def test_serialized(self):
        """
        Tests calling a CreditCard object's serialized function. This test evaluates if the dictionary serialized
        returns is correct.
        """
        credit_card = CreditCard(
            number="1234567890123456",
            is_valid=True,
            major_industry_identifier="1",
            issuer_identification_number="123456",
            personal_account_number="789012345",
            check_digit="6")
        res = credit_card.serialized()
        self.assertDictEqual(
            {
                "major_industry_identifier": "1",
                "issuer_identification_number": "123456",
                "personal_account_number": "789012345",
                "check_digit": "6",
                "is_valid": True
            }, res)

    def test_with_invalid_number(self):
        """
        Tests calling CreditCard.with_invalid_number with a string.
        """
        res = CreditCard.with_invalid_number("1234567890123456")
        self.assertEqual(res.is_valid, False)
        self.assertIsNone(res.major_industry_identifier)
        self.assertIsNone(res.issuer_identification_number)
        self.assertIsNone(res.personal_account_number)
        self.assertIsNone(res.check_digit)

    def test_generate_with_iin_greater_than_two_digits(self):
        """
        Tests CreditCard.generate_with_iin with an IIN that is too long.
        """
        iin = "123"
        self.assertRaises(InvalidIinError, CreditCard.generate_from_iin, iin)

    def test_generate_with_iin_less_than_one_digit(self):
        """
        Tests CreditCard.generate_with_iin with an IIN that is too short.
        """
        iin = ""
        self.assertRaises(InvalidIinError, CreditCard.generate_from_iin, iin)

    def test_generate_with_iin_non_numeric(self):
        """
        Tests CreditCard.generate_with_iin with an IIN that contains characters other than 0-9.
        """
        iin = "a"
        self.assertRaises(InvalidIinError, CreditCard.generate_from_iin, iin)

    def test_generate_with_iin_valid(self):
        """
        Tests CreditCard.generate_with_iin with a valid IIN :)
        """
        iin = "45"
        res = CreditCard.generate_from_iin(iin)
        self.assertEqual("45", res.number[:2])
        self.assertTrue(res.is_valid)

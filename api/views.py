from django.http import HttpResponse, JsonResponse
from django.views import View

from .exceptions import InvalidCardNumberError, InvalidIinError
from .constants import (
    NUMBER,
    VALIDATE_BAD_REQUEST_NONE,
    GENERATE_BAD_REQUEST_NONE
)
from .models import CreditCard

from logging import getLogger

LOG = getLogger(__name__)


def index(request: 'HttpRequest'):
    """
    Health endpoint.
    :param request: a Django request object.
    :return: a blank HTTP response.
    """
    return HttpResponse()


# Thought: If I was doing this again, I may abstract things into a CreditCardView. The GET function for this class
# would require two parameters: function and number. Function would correspond to a function in the CreditCard class,
# and number would be used to instantiate an instance of the class. I may also abstract the credit card's Number into
# a separate class, and have all validation functions for it live there.
class ValidateView(View):
    def get(self, request: 'HttpRequest'):
        """
        Validation endpoint. The request data will come in the form of a query parameter in the get request
        called *number*. If this argument is None, the view returns a 400 response to the client. The view will try
        to call CreditCard.from_number with *number* as an argument - If this returns false, the client will instantiate
        a dummy CreditCard object with is_valid set to False and return it to the client. If the instantiation happens
        correctly, then the instantiated CreditCard object is serialized and sent back to the user with a 200 status.

        :param request: A Django request object. The URL should include one query parameter, *number*.

            :Example:
            http://localhost:8000/api/validate?num=1234567890123456

        :return: A JSON response object.

            If no *number* is provided, then the response looks like:
            :Example:
            {
                "error": "You need to provide a number to this endpoint. Try again with number=1234567890123456."
            }

            If the *number* provided by the user is invalid, then the response looks like:
            :Example:
            {
                "is_valid": false,
                "major_industry_identifier": null,
                "issuer_identification_number": null,
                "personal_account_number": null,
                "check_digit": null
            }

            If the *number* provided by the user is valid, then the response looks like:
            :Example:
            {
                "is_valid": true,
                "major_industry_identifier": "1",
                "issuer_identification_number": "123456",
                "personal_account_number": "789012345",
                "check_digit": "6"
            }

        """
        LOG.info("I've received a request to validate a card number.")
        query_parameters = request.GET
        number = query_parameters.get(NUMBER)
        if number is None:
            LOG.warning("User sent a request with no number argument. I'm returning them a 400 response.")
            response = JsonResponse({"error": VALIDATE_BAD_REQUEST_NONE})
            response.status_code = 400
            return response
        try:
            credit_card = CreditCard.from_number(number)
        except InvalidCardNumberError:
            LOG.warning("User sent a request with something that isn't a credit card number."
                        " I'm returning them a 400 response.")
            credit_card = CreditCard.with_invalid_number(number)
            response = JsonResponse(credit_card.serialized())
            response.status_code = 400
            return response
        LOG.info("I've successfully validated the card number. I'm returning a response to the user now.")
        data = credit_card.serialized()
        LOG.debug(data)
        return JsonResponse(data)


class GenerateView(View):
    def get(self, request):
        """
        Generation endpoint. This endpoint expects that the client will include a query parameter *iin* in the URL.
        I then use *iin* in a call to CreditCard.generate_from_iin. If it works, I return the serialized CreditCard
        object. If *iin* is None, I immediately return a 400 response. If the CreditCard.generate_from_iin function
        gives me an InvalidIinError
        :param request: A Django request object. The URL should include one query parameter, *iin*.

            :Example:
            http://localhost:8000/api/generate?iin=45

        :return: A JsonResponse object.

            If *iin* is None or invalid, then the response looks like:
            :Example:
            {
                "error": "IINs should be only digits and either length one or two. Try 65!"
            }

            Otherwise the response for the URL above looks like:
            :Example:
            {
                "major_industry_identifier": "4",
                "issuer_identification_number": "453478",
                "personal_account_number": "220633364",
                "check_digit": "3",
                "is_valid": true
            }

        """
        LOG.info("I've received a request to generate a card number.")
        query_parameters = request.GET
        iin = query_parameters.get("iin")
        if iin is None:
            LOG.warning("User sent a request with no iin argument. I'm returning them a 400 response.")
            response = JsonResponse({"error": GENERATE_BAD_REQUEST_NONE})
            response.status_code = 400
            return response
        LOG.info(f"I found the IIN {iin}. I'm trying to generate the card number now.")
        try:
            credit_card = CreditCard.generate_from_iin(iin)
        except InvalidIinError:
            LOG.warning("The CreditCard class didn't like that IIN number. I'm letting the user know.")
            response = JsonResponse({"error": "IINs should be only digits and either length one or two. Try 65!"})
            response.status_code = 400
            return response
        LOG.info(f"I've successfully generated a card number for the client for IIN {iin}. "
                 f"I'm returning it to them now.")
        data = credit_card.serialized(with_number=True)
        LOG.debug(data)
        return JsonResponse(data)

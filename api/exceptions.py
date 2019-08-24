class InvalidCardNumberError(BaseException):
    """
    Raised when input to the from_number function in the CreditCard class finds a string that
        1. Is not numeric, or
        2. returns False when passed as an argument to pyluhn.verify.
    """
    pass


class InvalidIinError(BaseException):
    """
    Raised when an IIN is either less than length 1 or greater than length 16 or containing non-numeric characters.
    """
    pass

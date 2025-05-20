from jwt.exceptions import InvalidTokenError


class InvalidNotBeforeError(InvalidTokenError):
    pass


class InvalidExpirationError(InvalidTokenError):
    pass


class InvalidTokenTypeError(InvalidTokenError):
    pass

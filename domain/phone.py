import re

# official DDD (area code) list, as defined by Anatel.
VALID_DDDS = frozenset({
    11, 12, 13, 14, 15, 16, 17, 18, 19,
    21, 22, 24,
    27, 28,
    31, 32, 33, 34, 35, 37, 38,
    41, 42, 43, 44, 45, 46,
    47, 48, 49,
    51, 53, 54, 55,
    61,
    62, 64,
    63,
    65, 66,
    67,
    68,
    69,
    71, 73, 74, 75, 77,
    79,
    81, 87,
    82,
    83,
    84,
    85, 88,
    86, 89,
    91, 93, 94,
    92, 97,
    95,
    96,
    98, 99,
})

# First digit of a mobile subscriber number, before the mandatory "9"
# prefix was introduced nationwide. Used to tell mobile numbers apart
# from landlines when the "9" is missing.
_MOBILE_LEADING_DIGITS = frozenset("6789")

_DIGITS_ONLY_PATTERN = re.compile(r"^\d+$")

_LOCAL_NUMBER_LENGTHS = (10, 11)  # DDD (2) + subscriber number (8 or 9)


class PhoneValidationError(ValueError):
    """Raised when a phone number is invalid or cannot be normalized."""


def normalize_phone(raw_phone: str) -> str:
    """Validate a phone number and normalize it to DDD + 9-digit format.

    `raw_phone` is expected to contain only digits, including the DDD
    but not the country code (e.g. "11987654321" or "1187654321").

    Mobile numbers missing the mandatory leading "9" are corrected
    automatically whenever the subscriber number's first digit
    unambiguously identifies it as a mobile line (6, 7, 8 or 9).
    Landline numbers are rejected, since WhatsApp requires a mobile
    number in the "DDD + 9 + 8 digits" format.

    Returns:
        The phone number as DDD + 9 digits (11 digits total).

    Raises:
        PhoneValidationError: if the DDD or the subscriber number is
            invalid.
    """
    if not _DIGITS_ONLY_PATTERN.match(raw_phone):
        raise PhoneValidationError(
            f"telefone contém caracteres não numéricos: {raw_phone!r}"
        )

    if len(raw_phone) not in _LOCAL_NUMBER_LENGTHS:
        raise PhoneValidationError(
            "telefone deve ter 10 ou 11 dígitos (DDD + número): "
            f"{raw_phone!r}"
        )

    ddd, subscriber_number = int(raw_phone[:2]), raw_phone[2:]

    if ddd not in VALID_DDDS:
        raise PhoneValidationError(f"DDD inválido: {ddd}")

    if len(subscriber_number) == 9:
        if subscriber_number[0] != "9":
            raise PhoneValidationError(
                f"celular deve começar com 9 após o DDD: {raw_phone!r}"
            )
        return f"{ddd}{subscriber_number}"

    if subscriber_number[0] not in _MOBILE_LEADING_DIGITS:
        raise PhoneValidationError(
            f"número de fixo não é suportado pelo WhatsApp: {raw_phone!r}"
        )

    return f"{ddd}9{subscriber_number}"
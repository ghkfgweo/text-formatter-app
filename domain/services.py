from urllib.parse import quote

import pandas as pd

from domain.models import Contact, GeneratedLink, ParsingError, Separator
from domain.phone import PhoneValidationError, normalize_phone

APP_TITLE: str = "Gerador de Links do WhatsApp"
DEFAULT_TEMPLATE: str = "Bom dia, {name}! Tudo bem?"

COUNTRY_CODE: str = "55"


class ContactParsingError(ValueError):
    """Raised when a line cannot be parsed into a valid contact."""


def clean_line(line: str) -> str:
    """Collapse any run of whitespace in `line` into single spaces."""
    return " ".join(line.split())


def parse_contact(line: str) -> Contact:
    """Parse a single "name phone" line into a Contact.

    The phone number is expected to be the last token in the line.
    Extra/duplicated whitespace between tokens is normalized first.

    Raises:
        ContactParsingError: if the line is malformed or the phone
            number fails validation.
    """
    line = clean_line(line)

    if not line or " " not in line:
        raise ContactParsingError(
            "linha deve conter nome e telefone separados por espaço"
        )

    name_part, _, raw_phone = line.rpartition(" ")
    first_name = name_part.split(" ")[0]

    if not first_name:
        raise ContactParsingError("nome não encontrado na linha")

    try:
        local_phone = normalize_phone(raw_phone)
        
    except PhoneValidationError as error:
        raise ContactParsingError(str(error)) from error

    return Contact(name=first_name, phone=f"{COUNTRY_CODE}{local_phone}")


def render_message(template: str, contact: Contact) -> str:
    """Render the message template for a given contact."""
    return template.format(name=contact.name)


def generate_link(
    index: int,
    contact: Contact,
    template: str,
) -> GeneratedLink:
    """Build the WhatsApp link for a contact."""
    message = render_message(template, contact)
    encoded_message = quote(message)

    url = (
        f"https://wa.me/{contact.phone}"
        f"?text={encoded_message}"
    )

    return GeneratedLink(index=index, contact=contact, url=url)


def process_contacts(
    text: str,
    template: str,
) -> tuple[list[GeneratedLink], list[ParsingError]]:
    """Parse every non-blank line in `text` into links, keeping errors.

    Lines that fail to parse (bad format or invalid phone) are
    collected in the returned error list instead of interrupting the
    whole batch.
    """
    links: list[GeneratedLink] = []
    errors: list[ParsingError] = []

    for line in text.splitlines():
        if not line.strip():
            continue

        try:
            contact = parse_contact(line)
        except ContactParsingError as error:
            errors.append(ParsingError(line=line, reason=str(error)))
            continue

        index = len(links) + 1
        links.append(generate_link(index, contact, template))

    return links, errors


def format_results(
    links: list[GeneratedLink],
    separator: str = Separator.DOUBLE_NEWLINE,
) -> str:
    """Join generated links into a single text block for copying."""
    return separator.join(
        f"{link.index}. {link.contact.name} {link.url}"
        for link in links
    )


def build_results_dataframe(links: list[GeneratedLink]) -> pd.DataFrame:
    """Build a DataFrame with one row per generated link."""
    return pd.DataFrame([
        {
            "#": link.index,
            "Nome": link.contact.name,
            "Telefone": link.contact.phone,
            "URL": link.url,
        }
        for link in links
    ])
import pandas as pd
from urllib.parse import quote
from models import Contact, GeneratedLink


APP_TITLE: str = "Gerador de Links do WhatsApp"
DEFAULT_TEMPLATE: str = "Bom dia, {name}! Tudo bem?"


def parse_contact(line: str) -> Contact | None:
    line: str = line.strip()
    
    if not line:
        return None
    
    name, phone = line.rsplit(" ", maxsplit=1)
    
    name = " ".join(name.split()[:1])
    phone = f"55{phone}"
    
    return Contact(name=name, phone=phone)


def render_message(template: str, contact: Contact) -> str:
    return template.format(name=contact.name)


def generate_link(
        contact: Contact,
        template: str
    ) -> GeneratedLink:

    message = render_message(template, contact)
    encoded_message = quote(message)
    
    url = (
        f"https://wa.me/{contact.phone}"
        f"?text={encoded_message}"
    )

    return GeneratedLink(contact=contact, url=url)


def process_contacts(
    text: str,
    template: str
) -> tuple[list[GeneratedLink], list[str]]:
    
    links, errors = [], []
    
    for line in text.splitlines():
        if not line.strip():
            continue
        
        contact = parse_contact(line)
        
        if contact is None:
            errors.append(line)
            continue
        
        links.append(
            generate_link(contact, template)
        )
        
    return links, errors


def format_results(links: list[GeneratedLink]) -> str:
    return "\n\n".join(
        f"{link.contact.name} {link.url}"
        for link in links
    )
    
    
def build_results_dataframe(links: list[GeneratedLink]):
    return pd.DataFrame([
        {
            "Nome": link.contact.name,
            "Telefone": link.contact.phone,
            "URL": link.url,
        }
        for link in links
    ])
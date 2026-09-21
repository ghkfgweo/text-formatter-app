from dataclasses import dataclass


@dataclass(frozen=True)
class Contact:
    name: str
    phone: str
    

@dataclass(frozen=True)
class GeneratedLink:
    contact: Contact
    url: str
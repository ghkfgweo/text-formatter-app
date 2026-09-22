from dataclasses import dataclass
from enum import Enum


class Separator(str, Enum):
    DOUBLE_NEWLINE = "\n\n"
    SINGLE_NEWLINE = "\n"


@dataclass(frozen=True)
class Contact:
    name: str
    phone: str
    

@dataclass(frozen=True)
class GeneratedLink:
    index: int
    contact: Contact
    url: str
    
    
@dataclass(frozen=True)
class ParsingError:
    line: str
    reason: str

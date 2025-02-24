from typing import List
from typing import Optional

from pydantic import BaseModel

words = [
    {
        "en": "cat",
        "ru": "кошка"
    },
    {

        "en": "table",
        "ru": "стол",
        "es": "испанский стол"
    },
]


class Base(BaseModel):
    pass


class Word(Base):
    en: str | None = None
    ru: str | None = None
    es: str | None = None


print([Word(**word) for word in words])

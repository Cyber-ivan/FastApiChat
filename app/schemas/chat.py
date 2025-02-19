from pydantic import BaseModel


class CreateChatSchema(BaseModel):
    chat_name: str = "Noname"


class DeleteChatSchema(BaseModel):
    chat_id: int



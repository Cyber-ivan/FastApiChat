from pydantic import BaseModel, EmailStr
from typing import List


class CreateChatSchema(BaseModel):
    chat_name: str = "Noname"
    users: List[EmailStr]


class CreateChatResponseSchema(BaseModel):
    message: str
    chat_id: int


class DeleteChatSchema(BaseModel):
    chat_id: int


class DeleteChatResponseSchema(BaseModel):
    message: str


class NewMessageSchema(BaseModel):
    chat_id: int
    text: str


class GetMessagesSchema(BaseModel):
    chat_id: List[int] | None = None
    user_id: List[int] | None = None

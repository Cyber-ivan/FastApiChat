from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class ChatCreateSchema(BaseModel):
    name: str = "NonameChat"
    emails: Optional[List[EmailStr]] = []


class DeleteChatSchema(BaseModel):
    id: int


class NewMessageSchema(BaseModel):
    chat_id: int
    message: str

class GetMessagesSchema(BaseModel):
    chat_id: int

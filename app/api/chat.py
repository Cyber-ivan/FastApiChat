from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session

from app.dependency.auth import get_user_id_in_token
from app.dependency.database import get_db
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.models import User, Chat, UserChat, Message
from app.schemas.chat import (
    CreateChatSchema,
    DeleteChatSchema,
    CreateChatResponseSchema, DeleteChatResponseSchema, NewMessageSchema, GetMessagesSchema,

)

router = APIRouter(
    tags=["Chat"],
)


@router.post("/newchat", response_model=CreateChatResponseSchema)
async def add_chat(chat_data: CreateChatSchema, request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id_in_token(request.cookies.get("access_token"))
    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    current_user = result.scalars().first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    email_users = chat_data.users
    if current_user not in chat_data.users:
        email_users.append(current_user.email)
    users_stmt = select(User).where(User.email.in_(email_users))
    users_result = await db.execute(users_stmt)
    chat_users = users_result.scalars().all()
    new_chat = Chat(name=chat_data.chat_name, users=chat_users)
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return {
        "message": "Chat created successfully",
        "chat_id": new_chat.id,
    }


@router.delete("/deletechat", response_model=DeleteChatResponseSchema)
async def delete_chat(chat_data: DeleteChatSchema, request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id_in_token(request.cookies.get("access_token"))
    stmt = select(Chat).where(Chat.id == chat_data.chat_id)
    chat = await db.execute(stmt)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    stmt = select(UserChat).where(UserChat.chat_id == chat_data.chat_id, UserChat.user_id == int(user_id))
    current_user_in_chat = await db.execute(stmt)
    if not current_user_in_chat:
        raise HTTPException(status_code=403, detail="You are not a member of this chat")
    stmt = delete(UserChat).where(UserChat.chat_id == chat.id)
    await db.execute(stmt)
    await db.delete(chat)
    await db.commit()
    return {"message": "Chat deleted successfully"}


@router.post("/newmessage")
async def create_message(data: NewMessageSchema, request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id_in_token(request.cookies.get("access_token"))
    new_message = Message(user_id=user_id, chat_id=data.chat_id, text=data.text)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return {"message": "Message created successfully"}


@router.get("/messages")
async def get_messages(chat_data: GetMessagesSchema, request: Request, db: Session = Depends(get_db)):
    get_user_id_in_token(request.cookies.get("access_token"))
    stmt = select(Message)
    if chat_data.chat_id:
        stmt = select(Message).where(Message.chat_id.in_(chat_data.chat_id))
    if chat_data.user_id:
        stmt = stmt.where(Message.user_id.in_(chat_data.user_id))
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return {"messages": messages}
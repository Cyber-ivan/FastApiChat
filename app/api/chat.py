# from fastapi import APIRouter, Depends
# from app.schemas.chat import (
#     CreateChatSchema,
#     DeleteChatSchema,
#
# )
#
# router = APIRouter()
#
#
# @router.post("/user/addchat")
# async def add_chat(chat_data: CreateChatSchema, request: Request, db: Session = Depends(get_db)):
#     access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Access token not found")
#
#     payload = security._decode_token(access_token)
#     user_id = payload.sub
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
#     current_user = db.query(User).filter(User.id == int(user_id)).first()
#     if not current_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     new_chat = Chat(name=chat_data.name)
#     db.add(new_chat)
#     db.commit()
#     db.refresh(new_chat)
#
#     users = db.query(User).filter(User.email.in_(chat_data.emails)).all() if chat_data.emails else []
#
#     if current_user not in users:
#         users.append(current_user)
#
#     if not users:
#         raise HTTPException(status_code=400, detail="No valid users found")
#
#     user_chat_entries = [UserChat(user_id=user.id, chat_id=new_chat.id) for user in users]
#     db.add_all(user_chat_entries)
#
#     db.commit()
#
#     return {
#         "message": "Chat created successfully",
#         "chat_id": new_chat.id,
#         "users": [user.email for user in users]
#     }
#
#
# @router.delete("/user/deletechat")
# async def delete_chat(chat_data: DeleteChatSchema, request: Request, db: Session = Depends(get_db)):
#     access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Access token not found")
#
#     payload = security._decode_token(access_token)
#     user_id = int(payload.sub)  # Приводим к int
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
#     chat = db.query(Chat).filter(Chat.id == int(chat_data.id)).first()
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")
#
#     user_in_chat = db.query(UserChat).filter(
#         UserChat.chat_id == chat.id,
#         UserChat.user_id == user_id
#     ).first()
#
#     if not user_in_chat:
#         raise HTTPException(status_code=403, detail="You are not a member of this chat")
#
#     db.query(UserChat).filter(UserChat.chat_id == chat.id).delete(synchronize_session=False)
#
#     db.delete(chat)
#     db.commit()
#
#     return {"message": "Chat deleted successfully"}
#
#
# @router.post("/user/newmessage")
# async def create_message(message_data: NewMessageSchema, request: Request, db: Session = Depends(get_db)):
#     access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Access token not found")
#     payload = security._decode_token(access_token)
#     user_id = payload.sub
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     new_message = Message(user_id=user_id, chat_id=message_data.chat_id, text=message_data.message)
#     db.add(new_message)
#     db.commit()
#     db.refresh(new_message)
#     return {"message": "Message created successfully"}
#
#
# @router.get("/messages")
# def get_messages(
#         chat_data: GetMessagesSchema,
#         request: Request,
#         db: Session = Depends(get_db)
# ):
#     access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Access token not found")
#
#     payload = security._decode_token(access_token)
#     user_id = int(payload.sub)
#
#     messages = db.query(Message).filter(
#         Message.chat_id == chat_data.chat_id,
#         Message.user_id == user_id
#     ).all()
#
#     return {"messages": messages}

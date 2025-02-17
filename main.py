from fastapi import FastAPI, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from database import session_factory, Base, engine
from models import User, UserChat, Chat, Message
from schemes import UserCreateSchema, UserLoginSchema, ChatCreateSchema, DeleteChatSchema, NewMessageSchema, \
    GetMessagesSchema
import hashlib
from config import security, config

app = FastAPI()
Base.metadata.create_all(bind=engine)


def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@app.post("/auth/register")
async def createuser(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id, "email": new_user.email}


@app.post("/auth/login")
async def login(user: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        if hash_password(user.password) == existing_user.password:
            access_token = security.create_access_token(uid=str(existing_user.id))
            my_refresh_token = security.create_refresh_token(uid=str(existing_user.id))
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
            response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, my_refresh_token)
            return {"message": "Logged in successfully",
                    "access_token": access_token,
                    "refresh_token": my_refresh_token}
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/auth/refresh")
async def refresh_token(response: Response, request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get(config.JWT_REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    payload = security._decode_token(refresh_token)
    try:
        user_id = payload.sub
        existing_user = db.query(User).filter(User.id == int(user_id)).first()
        if not existing_user:
            raise HTTPException(status_code=401, detail="User not found")
        access_token = security.create_access_token(uid=str(existing_user.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
        return {"message": "Access token refreshed", "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    #     response.set_cookie(
    #         key="access_token",
    #         value=access_token,
    #         httponly=True,
    #         secure=True,
    #         samesite="Lax",
    #         max_age=3600  # 1 час
    #     )


@app.post("/auth/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    my_refresh_token = request.cookies.get(config.JWT_REFRESH_COOKIE_NAME)
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(config.JWT_REFRESH_COOKIE_NAME)
    return {"message": "Logged out successfully", "access_token": access_token}


@app.get("/users")
async def get_users(response: Response, request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")
    payload = security._decode_token(access_token)
    user_id = payload.sub
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"user_id": user.id, "username": user.username, "email": user.email}


@app.post("/user/addchat")
async def add_chat(chat_data: ChatCreateSchema, request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    payload = security._decode_token(access_token)
    user_id = payload.sub
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    current_user = db.query(User).filter(User.id == int(user_id)).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_chat = Chat(name=chat_data.name)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    users = db.query(User).filter(User.email.in_(chat_data.emails)).all() if chat_data.emails else []

    if current_user not in users:
        users.append(current_user)

    if not users:
        raise HTTPException(status_code=400, detail="No valid users found")

    user_chat_entries = [UserChat(user_id=user.id, chat_id=new_chat.id) for user in users]
    db.add_all(user_chat_entries)

    db.commit()

    return {
        "message": "Chat created successfully",
        "chat_id": new_chat.id,
        "users": [user.email for user in users]
    }


@app.delete("/user/deletechat")
async def delete_chat(chat_data: DeleteChatSchema, request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    payload = security._decode_token(access_token)
    user_id = int(payload.sub)  # Приводим к int
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    chat = db.query(Chat).filter(Chat.id == int(chat_data.id)).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_in_chat = db.query(UserChat).filter(
        UserChat.chat_id == chat.id,
        UserChat.user_id == user_id
    ).first()

    if not user_in_chat:
        raise HTTPException(status_code=403, detail="You are not a member of this chat")

    # Удаляем все связи пользователей с этим чатом в UserChat
    db.query(UserChat).filter(UserChat.chat_id == chat.id).delete(synchronize_session=False)

    # Удаляем сам чат
    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}


@app.post("/user/newmessage")
async def create_message(message_data: NewMessageSchema, request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")
    payload = security._decode_token(access_token)
    user_id = payload.sub
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    new_message = Message(user_id=user_id, chat_id=message_data.chat_id, text=message_data.message)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return {"message": "Message created successfully"}


@app.get("/messages")
def get_messages(
        chat_data: GetMessagesSchema,
        request: Request,
        db: Session = Depends(get_db)
):
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found")

    payload = security._decode_token(access_token)
    user_id = int(payload.sub)

    # Фильтрация сразу по chat_id и user_id
    messages = db.query(Message).filter(
        Message.chat_id == chat_data.chat_id,
        Message.user_id == user_id
    ).all()

    return {"messages": messages}


def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)


if __name__ == "__main__":
    main()

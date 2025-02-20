from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.dependency.database import get_db
from app.dependency.auth import get_password_hash, verify_password
from app.models.models import User, Chat, UserChat, Message
from sqlalchemy.future import select
from app.core.security import create_refresh_token, create_access_token, decode_token
from app.schemas.auth import (
    CreateUserSchema,
    UserResponse,
    LoginUserSchema,
    LoginResponseSchema,
    LogoutResponseSchema,
    RefreshTokenResponseSchema
)

router = APIRouter(
    tags=["Auth"],
)


@router.post("/register", response_model=UserResponse)
async def createuser(user: CreateUserSchema, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "name": new_user.username}


@router.post("/login", response_model=LoginResponseSchema)
async def login(user: LoginUserSchema, response: Response, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    current_user = result.scalars().first()
    if current_user:
        if verify_password(user.password, current_user.password):
            access_token = create_access_token(
                data={"sub": str(current_user.id)}
            )
            refresh_token = create_refresh_token(
                data={"sub": str(current_user.id)}
            )
            response.set_cookie("access_token", access_token)
            response.set_cookie("refresh_token", refresh_token)
            return {"message": "Logged in successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token}
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/refresh", response_model=RefreshTokenResponseSchema)
async def refresh_token(response: Response, request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    payload = decode_token(refresh_token)
    try:
        user_id = payload.get("sub")
        stmt = select(User).where(User.id == int(user_id))
        result = await db.execute(stmt)
        current_user = result.scalars().first()
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")
        access_token = create_access_token(
            data={"sub": str(current_user.id)}
        )
        response.set_cookie("access_token", access_token)
        response.set_cookie("refresh_token", refresh_token)
        return {"message": "Access token refreshed", "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/logout", response_model=LogoutResponseSchema)
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
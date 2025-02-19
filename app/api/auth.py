from fastapi import APIRouter, Depends, HTTPException,Response
from sqlalchemy.orm import Session
from app.dependency.database import get_db
from app.dependency.auth import get_password_hash, verify_password
from app.models.models import User, Chat, UserChat, Message
from sqlalchemy.future import select
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


@router.post("/auth/login", response_model=LoginResponseSchema)
async def login(user: LoginUserSchema, response: Response, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        if verify_password(get_password_hash(existing_user.password), user.password):
            access_token = security.create_access_token(uid=str(existing_user.id))
            my_refresh_token = security.create_refresh_token(uid=str(existing_user.id))
            response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
            response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, my_refresh_token)
            return {"message": "Logged in successfully",
                    "access_token": access_token,
                    "refresh_token": my_refresh_token}
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")


# @router.post("/auth/refresh", response_model=RefreshTokenResponseSchema)
# async def refresh_token(response: Response, request: Request, db: Session = Depends(get_db)):
#     refresh_token = request.cookies.get(config.JWT_REFRESH_COOKIE_NAME)
#     if not refresh_token:
#         raise HTTPException(status_code=401, detail="Refresh token not found")
#     payload = security._decode_token(refresh_token)
#     try:
#         user_id = payload.sub
#         existing_user = db.query(User).filter(User.id == int(user_id)).first()
#         if not existing_user:
#             raise HTTPException(status_code=401, detail="User not found")
#         access_token = security.create_access_token(uid=str(existing_user.id))
#         response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
#         return {"message": "Access token refreshed", "access_token": access_token}
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
#     #     response.set_cookie(
#     #         key="access_token",
#     #         value=access_token,
#     #         httponly=True,
#     #         secure=True,
#     #         samesite="Lax",
#     #         max_age=3600  # 1 час
#     #     )
#
#
# @router.post("/auth/logout", response_model=LogoutResponseSchema)
# async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
#     my_refresh_token = request.cookies.get(config.JWT_REFRESH_COOKIE_NAME)
#     access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
#     response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
#     response.delete_cookie(config.JWT_REFRESH_COOKIE_NAME)
#     return {"message": "Logged out successfully", "access_token": access_token}

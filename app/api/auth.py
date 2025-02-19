from fastapi import APIRouter, Depends
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


def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserResponse)
async def createuser(user: CreateUserSchema, db: Session = Depends(get_db)):
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


@router.post("/auth/login", response_model=LoginResponseSchema)
async def login(user: LoginUserSchema, response: Response, db: Session = Depends(get_db)):
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


@router.post("/auth/refresh", response_model=RefreshTokenResponseSchema)
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


@router.post("/auth/logout", response_model=LogoutResponseSchema)
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    my_refresh_token = request.cookies.get(config.JWT_REFRESH_COOKIE_NAME)
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(config.JWT_REFRESH_COOKIE_NAME)
    return {"message": "Logged out successfully", "access_token": access_token}

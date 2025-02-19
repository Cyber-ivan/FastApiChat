from pydantic import BaseModel, EmailStr


class CreateUserSchema(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    message: str
    class Config:
        from_attributes = True

class LogoutResponseSchema(BaseModel):
    message: str

class RefreshTokenResponseSchema(BaseModel):
    message: str
    access_token: str
# from fastapi import APIRouter, Depends
#
# router = APIRouter()
#
# @app.get("/users")
# async def get_users(response: Response, request: Request, db: Session = Depends(get_db)):
#     access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Access token not found")
#     payload = security._decode_token(access_token)
#     user_id = payload.sub
#     user = db.query(User).filter(User.id == int(user_id)).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
#     return {"user_id": user.id, "username": user.username, "email": user.email}
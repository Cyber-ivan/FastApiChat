from fastapi import FastAPI
from app.api import auth, chat, users

app = FastAPI(
    title="Simple chat",
    version="0.0.1",
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# app.include_router(chat.router, prefix="/chat", tags=["Chat"])
# app.include_router(users.router, prefix="/users", tags=["Users"])

def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)

if __name__ == "__main__":
    main()
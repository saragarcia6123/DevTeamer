from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import users_router, auth_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(users_router, prefix='/users')
app.include_router(auth_router)
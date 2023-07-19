from app.internal import stripe_module

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://app.revenut.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins
)

@app.get("/", status_code=status.HTTP_404_NOT_FOUND)
async def read_root():
	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.get("/health", status_code=status.HTTP_200_OK)
async def read_health():
    return {"Hello": "World!"}

if __name__ == "__main__":
    print("main")
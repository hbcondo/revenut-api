import uvicorn

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
async def read_root() -> None:
    """
    Root request
    """
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.get("/health", status_code=status.HTTP_200_OK)
async def read_health() -> bool:
    """
    API health check request
    """
    return True

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
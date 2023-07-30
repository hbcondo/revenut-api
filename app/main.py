import uvicorn

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from internal.stripe_module import RevenutStripe

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

@app.get("/v1/dashboard", response_model=RevenutStripe, status_code=status.HTTP_401_UNAUTHORIZED)
async def read_account(
    response: Response
    , tzIdentifier: str
    , code: str | None = None
    , account: str | None = None
):
    rStripe = RevenutStripe()

    if (code):
        rStripe = RevenutStripe(AuthorizationCode=code)
        
        if (rStripe.IsAuthorized):
            rStripe = RevenutStripe(AccountID=rStripe.AccountID, TimezonePreference=tzIdentifier)

    if (account):
        rStripe = RevenutStripe(AccountID=account, TimezonePreference=tzIdentifier)

    if (rStripe.AccountName):
        response.status_code = status.HTTP_200_OK

    return rStripe

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
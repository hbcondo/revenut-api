import asyncio

from hypercorn.config import Config
from hypercorn.asyncio import serve

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from internal.stripe_module import RevenutStripe
from internal.enums import RevenutAuthorizationType

app = FastAPI(
    title="Revenut API",
    description="This is an API that delivers RESTful endpoints to power the SaaS analytics web + mobile app Revenut",
    version="1.0",
    contact={
        "name": "@hbcondo",
        "url": "https://github.com/hbcondo/revenut-api"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://github.com/hbcondo/revenut-api/blob/e24853c36326820a99c21f21c40306a20ca14923/LICENSE"
    }
)

origins = [
    "https://app.revenut.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins
)

"""
If you are using a third party library that communicates with something 
(a database, an API, the file system, etc.) and doesn't have support for using await, 
then declare your path operation functions as normally, with just def

Source: https://fastapi.tiangolo.com/async/
"""

@app.get("/", status_code=status.HTTP_404_NOT_FOUND, summary="Root")
def read_root() -> None:
    """
    Root request
    """
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@app.get("/health", status_code=status.HTTP_200_OK, summary="Health check")
def read_health() -> bool:
    """
    API health check request
    """
    return True

@app.get("/v1/dashboard", response_model=RevenutStripe, status_code=status.HTTP_401_UNAUTHORIZED, summary="SaaS metrics")
def read_account(
    response: Response
    , tzIdentifier: str
    , code: str | None = None
    , account: str | None = None
) -> RevenutStripe:
    """
    Returns SaaS metrics as a populated ```RevenutStripe``` object
    - **tzIdentifier**: Timezone identifier https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    - **code**: Authorization code returned by OAuth provider
    - **account**: Account identifier returned by OAuth provider
    """

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

@app.get("/v1/logout", response_model=RevenutStripe, status_code=status.HTTP_401_UNAUTHORIZED, summary="Logout")
def read_logout(
    response: Response
    , account: str
) -> RevenutStripe:
    """
    Revokes access to requested account
    - **account**: Account identifier
    """

    rStripe = RevenutStripe()
    account_id = rStripe.revoke(account)

    if (account_id):
        rStripe.Status = RevenutAuthorizationType.REVOKED
        response.status_code = status.HTTP_200_OK

    return rStripe

if __name__ == "__main__":
    config = Config()
    config.bind = ["localhost:8000"]
    asyncio.run(serve(app, config))
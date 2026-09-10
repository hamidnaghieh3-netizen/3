from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from app.routers.auth import router as auth_router
from app.routers.auctions import router as auctions_router
from app.routers.bids import bids_router
from app.routers.lots import lots_router
from app.routers.invoices import router as invoices_router

from app import live_bidding




app = FastAPI(
    title="LiveAuction API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": False}
)

# ⭐ ROUTERS MUST BE INCLUDED BEFORE custom_openapi
app.include_router(auth_router)
app.include_router(auctions_router)
app.include_router(lots_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(invoices_router)
app.include_router(bids_router)
app.include_router(live_bidding.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="LiveAuction API",
        version="1.0.0",
        description="LiveAuction backend API",
        routes=app.routes,
    )

    # ❗️ REMOVE ALL MANUAL SECURITY SCHEME INJECTION
    # FastAPI already generates the correct Bearer scheme automatically.

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi





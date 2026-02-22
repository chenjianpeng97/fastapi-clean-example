from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.infrastructure.persistence_sqla.mappings.all import map_tables
from app.presentation.http.auth.asgi_middleware import (
    ASGIAuthMiddleware,
)
from app.presentation.http.controllers.root_router import create_root_router
from app.setup.config.settings import AppSettings
from app.setup.ioc.provider_registry import get_providers


def create_ioc_container(
    settings: AppSettings,
    *di_providers: Provider,
) -> AsyncContainer:
    return make_async_container(
        *get_providers(),
        *di_providers,
        context={AppSettings: settings},
    )


def create_web_app(settings: AppSettings) -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )
    # https://github.com/encode/starlette/discussions/2451
    app.add_middleware(ASGIAuthMiddleware)
    # CORSMiddleware must be added last so it is outermost (runs before auth)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    # Good place to register global exception handlers
    app.include_router(create_root_router())
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # https://dishka.readthedocs.io/en/stable/integrations/fastapi.html
    container = app.state.dishka_container
    try:
        map_tables()
        yield
    finally:
        await container.close()

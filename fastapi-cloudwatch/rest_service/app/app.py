from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from rest_service.logger import setup_logging
from rest_service.middlewares import RequestContextLogMiddleware
from rest_service.router import APIRouter
from rest_service.schema import ApiInfoSchema
from rest_service.api.monitor import router as monitor_router


def create_app(settings) -> FastAPI:
    """
    Creates the App
    :param settings:
    :return:
    """
    # First setup logging
    setup_logging()

    # Creating app
    api = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
        root_path=settings.root_path,
        openapi_url=settings.openapi_url
    )

    if settings.force_https:
        api.add_middleware(HTTPSRedirectMiddleware)

    api.add_middleware(RequestContextLogMiddleware)

    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    router = APIRouter()

    @router.get('/info', summary="Information", description="Obtain API information", response_model=ApiInfoSchema)
    async def welcome():
        return {'message': f'Welcome to {settings.app_title}',
                'name': settings.app_title,
                'version': settings.app_version,
                'api_version': settings.api_version}


    @router.get('/healthz')
    async def healthz():
        return f'{settings.api_version}: {settings.app_title}'

    # Adding all routes to the api
    for r in APIRouter.get_routes():
        api.include_router(r)
    return api

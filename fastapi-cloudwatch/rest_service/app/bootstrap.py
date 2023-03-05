import typing
import inject

from rest_service.settings import Settings
from . import dependency


def _init_app():
    from rest_service.app.app import create_app

    _api = create_app(typing.cast(Settings, inject.instance(Settings)))
    return _api


# Create the FAST API app
api = _init_app()

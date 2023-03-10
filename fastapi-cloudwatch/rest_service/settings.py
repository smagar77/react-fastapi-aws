import typing

import rest_service.__about__ as __about__


class Settings:
    """"""
    app_title: str = __about__.__NAME__
    app_version: str = __about__.__VERSION__
    api_version: str = __about__.__API_VERSION__
    app_description: str = __about__.__DESCRIPTION__

    app_port: int = 8080
    app_host: str = '127.0.0.1'
    app_base_url: str = None
    base_url: str = None
    root_path: str = ""
    openapi_url: str = '/openapi.json'
    current_env: str = 'LOCAL'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    token_url: str = 'token'
    log_file: str = '../app.logs'
    shared_secret_key: str = None
    app_secret_key: str = None

    force_https: bool = False
    cors_origins: typing.Set[str] = {"http://127.0.0.1:8080", "http://127.0.0.1:3000"}

    db_server: str = None
    db_user: str = None
    db_pass: str = None
    db_name: str = None
    sqlalchemy_uri: str = 'sqlite:///../../cache.db'

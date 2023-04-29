import sys
from os.path import abspath, join

# Adjust the paths
sys.path.insert(0, abspath(join(__file__, "../", "../")))

import inject
import uvicorn  # type: ignore

# Run the ASGI server
from settings import Settings
from rest_service.app.bootstrap import api

settings = inject.instance(Settings)

if __name__ == '__main__':
    uvicorn.run(
        api, host=settings.app_host, port=settings.app_port
    )

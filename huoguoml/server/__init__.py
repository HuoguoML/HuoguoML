import os

import pkg_resources
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.staticfiles import StaticFiles

from huoguoml.server.database.service import Service
from huoguoml.server.routers import experiment, run, ml_service


def start_huoguoml_server(artifact_dir: str, host: str, port: int):
    """
    Starts the HuoguoML server

    Args:
        artifact_dir: Location of the artifact directory
        host: The network address to listen on
        port: The port to listen on
    """
    service = Service(artifact_dir=artifact_dir)

    dashboard_files_dir = os.path.join(os.path.dirname(__file__),
                                       "dashboard",
                                       "build")

    app = FastAPI()

    origins = [
        "*",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(experiment.get_router(service=service))
    app.include_router(run.get_router(service=service))
    app.include_router(ml_service.get_router(service=service))

    app.mount("/",
              StaticFiles(directory=dashboard_files_dir, html=True),
              name="static")

    @app.exception_handler(404)
    async def http_exception_handler(request, exc):
        print("test")
        return RedirectResponse("/")

    @app.get("")
    async def get_experiments():
        return HTMLResponse(pkg_resources.resource_string(__name__, 'dashboard/build/index.html'))

    # @app.get("/", include_in_schema=True)
    # def root():
    #     return HTMLResponse(pkg_resources.resource_string(__name__, 'dashboard/build'))
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    start_huoguoml_server("../../examples/huoguoml", "127.0.0.1", 8080)

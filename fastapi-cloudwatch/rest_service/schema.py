from pydantic import BaseModel, Field


class ApiInfoSchema(BaseModel):
    name: str = Field(..., title="Name", description="Name of the app")
    version: str = Field(..., title="Version", description="Version of the app")
    api_version: str = Field(..., title="API Version", description="Version of the API")
    message: str = Field(..., title="Message", description="Welcome message")
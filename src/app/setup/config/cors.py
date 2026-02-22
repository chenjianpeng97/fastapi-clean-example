from pydantic import BaseModel, Field


class CorsSettings(BaseModel):
    allow_origins: list[str] = Field(alias="ALLOW_ORIGINS")
    allow_credentials: bool = Field(alias="ALLOW_CREDENTIALS", default=True)
    allow_methods: list[str] = Field(alias="ALLOW_METHODS", default=["*"])
    allow_headers: list[str] = Field(alias="ALLOW_HEADERS", default=["*"])

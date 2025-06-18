from pydantic_settings import BaseSettings, SettingsConfigDict

class PaginationSettings(BaseSettings):
    default_page: int = 1
    default_size: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="allow")
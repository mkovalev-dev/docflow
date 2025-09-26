from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError, BaseModel, AnyUrl, Field, field_validator


class HttpServer(BaseModel):
    """Параметры API сервера (uvicorn/gunicorn)"""

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = False

class Database(BaseModel):
    """База данных"""

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    database_url: str = ""
    ECHO: bool = False

class HttpClient(BaseModel):
    """Единые таймауты/ретраи для внешних HTTP клиентов (httpx)"""

    CONNECT_TIMEOUT_S: float = 2.0
    READ_TIMEOUT_S: float = 8.0
    WRITE_TIMEOUT_S: float = 8.0
    POOL_LIMIT: int = 100
    RETRIES: int = 2

class Services(BaseModel):
    """Внешние сервисы"""

    USERS_SERVICE_URL: AnyUrl = "http://localhost:8001/api"
    FILES_SERVICE_URL: AnyUrl = "http://localhost:8002/api"

class RedisCache(BaseModel):
    """Redis ля кэширования токенов сессий и др"""

    URL: str = "redis://127.0.0.1:6379/0"
    NAMESPACE: str = "default"
    DEFAULT_TTL_S: int = 300

class Pagination(BaseModel):
    DEFAULT_LIMIT: int = 15
    MAX_LIMIT: int = 50

class Settings(BaseSettings):
    """Главные настройки"""

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", extra="ignore"
    )

    DEBUG: bool = False
    SERVICE_NAME: str = "default"
    API_V1_PREFIX: str = "/api"
    TIMEZONE: str = "Europe/Moscow"

    http: HttpServer = HttpServer()
    db: Database
    http_client:HttpClient = HttpClient()
    services: Services = Services()
    redis: RedisCache = RedisCache()
    pagination: Pagination = Pagination()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.db.database_url:
            self.db.database_url = (
                f"postgresql+asyncpg://{self.db.POSTGRES_USER}:"
                f"{self.db.POSTGRES_PASSWORD}@"
                f"{self.db.POSTGRES_SERVER}:{self.db.POSTGRES_PORT}/"
                f"{self.db.POSTGRES_DB}"
            )

    def validate_required(self) -> None:
        """Явная проверка критичных параметров при старте"""
        pass



def get_settings() -> Settings:
    s = Settings()
    try:
        s.validate_required()
    except ValidationError as e:
        raise
    return s
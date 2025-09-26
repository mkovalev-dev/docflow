from logging.config import fileConfig
import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.core.settings import get_settings
from src.core.db import Base

from src.modules.registration.models import RegistrationNumber
from src.modules.documents.models import (
    Document,
    DocumentRegistration,
    DocumentAddress,
    DocumentConfidential,
    DocumentAccess,
)

from src.modules.workflow.models import Workflow, WorkflowStep, WorkflowParticipant

# Alembic Config object, предоставляет доступ к данным из alembic.ini
config = context.config

# Логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Загружаем настройки проекта
settings = get_settings()

# Подменяем URL из настроек
config.set_main_option("sqlalchemy.url", settings.db.database_url)

# Метаданные моделей для генерации миграций
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций в offline-режиме (генерация SQL без подключения)."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    """Выполняем миграции внутри транзакции."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запуск миграций в online-режиме (через async engine)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


main()

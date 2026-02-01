from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from alembic import command
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def make_alembic_config(uri: str, folder: str) -> Config:
    """Create a configured :class:`alembic.config.Config` object."""
    config = Config()
    config.set_main_option("script_location", folder)
    config.set_main_option("sqlalchemy.url", uri)
    return config


class _MigrationResult:
    """Provide backward compatibility for the `prepare_schema_from_migrations` function.

    By returning an instance of this class, the `prepare_schema_from_migrations` function
    can support both function and context manager usage.

    This is an internal class and is not part of the public API.
    """

    def __init__(self, engine: Engine, script: ScriptDirectory):
        self.engine = engine
        self.script = script

    def __iter__(self) -> Any:
        """Support unpacking: engine, script = prepare_schema_from_migrations(...)"""
        return iter((self.engine, self.script))

    def __enter__(self) -> tuple[Engine, ScriptDirectory]:
        """Support context manager usage"""
        return self.engine, self.script

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.engine.dispose()


def prepare_schema_from_migrations(
    uri: str, config: Config, revision: str = "head"
) -> _MigrationResult:
    """Applies migrations to a database.

    Can be used as both a function and a context manager:

    As a function:
        engine, script = prepare_schema_from_migrations(uri, config, revision="head")

    As a context manager (which will dispose the engine on exit):
        with prepare_schema_from_migrations(uri, config, revision="head") as (engine, script):
            # use engine and script
    """
    engine = create_engine(uri)
    script = ScriptDirectory.from_config(config)
    command.upgrade(config, revision)

    return _MigrationResult(engine, script)


def get_current_revision(
    config: Config, engine: Engine, script: ScriptDirectory
) -> str | tuple[str, ...] | None:
    """Get the current revision of a set of migrations."""
    return _get_revision(config, engine, script, revision_type="current")


def get_head_revision(
    config: Config, engine: Engine, script: ScriptDirectory
) -> str | tuple[str, ...] | None:
    """Get the head revision of a set of migrations."""
    return _get_revision(config, engine, script, revision_type="head")


def _get_revision(
    config: Config, engine: Engine, script: ScriptDirectory, revision_type: str
) -> str | tuple[str, ...] | None:
    with engine.connect() as conn:
        with EnvironmentContext(config, script) as env_context:
            env_context.configure(conn, version_table="alembic_version")
            if revision_type == "head":
                revision = env_context.get_head_revision()
            else:
                migration_context = env_context.get_context()
                revision = migration_context.get_current_revision()
    return revision


@contextmanager
def session_for_engine(engine: Engine) -> Generator[Session, None, None]:
    """Create a session for an engine.

    The session is closed when the context manager exits. This tool is useful for testing,
    for example to verify the application of a migration in detail. You might need to get two
    different session instances to use before and after the application of a migration.
    """
    session_cls = sessionmaker(bind=engine)
    session = session_cls()
    try:
        yield session
    finally:
        session.close()

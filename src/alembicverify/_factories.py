import warnings
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from alembic.config import Config
from sqlalchemy_utils import create_database, drop_database

from alembicverify.util import make_alembic_config


def create_alembic_config_fixture_factory(
    deprecated: bool = False,
) -> Callable[..., Callable[[pytest.FixtureRequest], Config]]:
    """Create a factory for creating alembic config fixtures."""

    def factory(
        alembic_db_uri_fixture_name: str = "alembic_db_uri",
        alembic_ini_location_fixture_name: str = "alembic_ini_location",
        **fixture_kwargs: Any,
    ) -> Callable[[pytest.FixtureRequest], Config]:
        """Create an alembic config fixture."""
        fixture_kwargs.setdefault("name", "alembic_config")

        @pytest.fixture(**fixture_kwargs)
        def fixture(request: pytest.FixtureRequest) -> Config:
            """Create an alembic config."""

            if deprecated:
                fixture_name = fixture_kwargs["name"]
                warnings.warn(
                    f"{fixture_name} is deprecated.",
                    DeprecationWarning,
                    stacklevel=2,
                )

            db_uri: str = request.getfixturevalue(alembic_db_uri_fixture_name)
            alembic_ini_location: str = request.getfixturevalue(alembic_ini_location_fixture_name)
            config = Config(alembic_ini_location)
            script_location: str | None = config.get_section_option("alembic", "script_location")
            return make_alembic_config(db_uri, script_location or "")

        fixture.__name__ = fixture_kwargs["name"]
        return fixture

    return factory


def create_db_fixture_factory(
    deprecated: bool = False,
) -> Callable[..., Callable[[pytest.FixtureRequest], Generator[None, None, None]]]:
    """Create a factory for creating database fixtures."""

    def factory(
        alembic_db_uri_fixture_name: str = "alembic_db_uri", **fixture_kwargs: Any
    ) -> Callable[[pytest.FixtureRequest], Generator[None, None, None]]:
        """Create a database fixture."""
        fixture_kwargs.setdefault("name", "new_db")

        @pytest.fixture(**fixture_kwargs)
        def fixture(request: pytest.FixtureRequest) -> Generator[None, None, None]:
            """Create a new database."""

            if deprecated:
                fixture_name = fixture_kwargs["name"]
                warnings.warn(
                    f"{fixture_name} is deprecated.",
                    DeprecationWarning,
                    stacklevel=2,
                )

            db_uri: str = request.getfixturevalue(alembic_db_uri_fixture_name)
            with _new_db(db_uri):
                yield

        fixture.__name__ = fixture_kwargs["name"]
        return fixture

    return factory


@contextmanager
def _new_db(db_uri: str) -> Generator[None, None, None]:
    create_database(db_uri)
    yield
    drop_database(db_uri)


## FIXTURE FACTORIES

alembic_config_factory = create_alembic_config_fixture_factory()
alembic_config_deprecated_factory = create_alembic_config_fixture_factory(deprecated=True)

new_db_factory = create_db_fixture_factory()
new_db_deprecated_factory = create_db_fixture_factory(deprecated=True)

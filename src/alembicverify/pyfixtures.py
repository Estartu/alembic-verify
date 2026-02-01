from ._factories import (
    alembic_config_deprecated_factory,
    alembic_config_factory,
    new_db_deprecated_factory,
    new_db_factory,
)


## MAIN FIXTURES

alembic_new_db = new_db_factory(alembic_db_uri_fixture_name="alembic_db_uri", name="alembic_new_db")

alembic_config = alembic_config_factory(
    alembic_db_uri_fixture_name="alembic_db_uri",
    alembic_ini_location_fixture_name="alembic_ini_location",
    name="alembic_config",
)

# DEPRECATED FIXTURES
new_db_left = new_db_deprecated_factory(alembic_db_uri_fixture_name="uri_left", name="new_db_left")
new_db_right = new_db_deprecated_factory(
    alembic_db_uri_fixture_name="uri_right", name="new_db_right"
)

alembic_config_left = alembic_config_deprecated_factory(
    alembic_db_uri_fixture_name="uri_left",
    alembic_ini_location_fixture_name="alembic_ini_location",
    name="alembic_config_left",
)

alembic_config_right = alembic_config_deprecated_factory(
    alembic_db_uri_fixture_name="uri_right",
    alembic_ini_location_fixture_name="alembic_ini_location",
    name="alembic_config_right",
)

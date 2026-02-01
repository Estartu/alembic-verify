from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture(scope="module")
def alembic_ini_location():
    """Return the location of the alembic.ini file."""
    return Path(__file__).parent.parent.parent / "alembic.ini"


def get_temporary_uri(uri):
    """Substitutes the database name with a random one.

    For example, given this uri:
    "mysql+mysqlconnector://root:@localhost/database_name"

    a call to ``get_temporary_uri(uri)`` could return something like this:
    "mysql+mysqlconnector://root:@localhost/temp_000da...898fe"

    where the last part of the name is taken from a unique ID in hex
    format.
    """
    base, _ = uri.rsplit("/", 1)
    uri = f"{base}/temp_{uuid4().hex}"
    return uri

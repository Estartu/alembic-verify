"""Test utilities."""

from contextlib import contextmanager
from unittest import TestCase

from sqlalchemy.orm import sessionmaker


Case = TestCase()
# "Diff is 4452 characters long. Set self.maxDiff to None to see it". Okay:
Case.maxDiff = None
assert_items_equal = Case.assertCountEqual


@contextmanager
def session_for_engine(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

from unittest.mock import call, patch

import pytest


pytest_plugins = "pytester"


@pytest.fixture(autouse=True)
def conftest(pytester):
    pytester.makeconftest(
        """
        import pytest

        @pytest.fixture
        def alembic_db_uri():
            return "db_uri"

        @pytest.fixture
        def alembic_ini_location():
            return "alembic.ini"

        # Deprecated fixtures

        @pytest.fixture
        def uri_left():
            return "left"

        @pytest.fixture
        def uri_right():
            return "right"
        """
    )


@pytest.fixture
def make_alembic_config_mock():
    with patch("alembicverify._factories.make_alembic_config") as m:
        yield m


@pytest.fixture
def Config_mock():
    with patch("alembicverify._factories.Config") as m:
        yield m


@pytest.fixture
def create_database_mock():
    with patch("alembicverify._factories.create_database") as m:
        yield m


@pytest.fixture
def drop_database_mock():
    with patch("alembicverify._factories.drop_database") as m:
        yield m


def test_alembic_config(Config_mock, make_alembic_config_mock, pytester):
    pytester.makepyfile(
        """
        def test_alembic_config(alembic_config):
            pass
        """
    )
    result = pytester.runpytest()
    assert result.ret == 0

    assert Config_mock.call_args_list == [call("alembic.ini")]
    assert make_alembic_config_mock.call_args_list == [
        call("db_uri", Config_mock.return_value.get_section_option.return_value)
    ]


def test_alembic_new_db(drop_database_mock, create_database_mock, pytester):
    pytester.makepyfile(
        """
        def test_new_db(alembic_new_db):
            pass
        """
    )
    result = pytester.runpytest()
    assert result.ret == 0

    assert create_database_mock.call_args_list == [call("db_uri")]
    assert drop_database_mock.call_args_list == [call("db_uri")]


# TESTS FOR DEPRECATED FIXTURES


class TestAlembicConfigLeft:
    @pytest.fixture(autouse=True)
    def create_test_file(self, pytester):
        pytester.makepyfile(
            """
            def test_config_left(alembic_config_left):
                pass
            """
        )

    def test_alembic_config_left(self, Config_mock, make_alembic_config_mock, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        assert Config_mock.call_args_list == [call("alembic.ini")]
        assert make_alembic_config_mock.call_args_list == [
            call("left", Config_mock.return_value.get_section_option.return_value)
        ]

    @pytest.mark.usefixtures("Config_mock", "make_alembic_config_mock")
    def test_alembic_config_left_issues_deprecation_warning(self, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        deprecation_warning = "DeprecationWarning: alembic_config_left is deprecated."
        assert deprecation_warning in result.stdout.str()


class TestAlembicConfigRight:
    @pytest.fixture(autouse=True)
    def create_test_file(self, pytester):
        pytester.makepyfile(
            """
            def test_config_right(alembic_config_right):
                pass
            """
        )

    def test_alembic_config_right(self, Config_mock, make_alembic_config_mock, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        assert Config_mock.call_args_list == [call("alembic.ini")]
        assert make_alembic_config_mock.call_args_list == [
            call("right", Config_mock.return_value.get_section_option.return_value)
        ]

    @pytest.mark.usefixtures("Config_mock", "make_alembic_config_mock")
    def test_alembic_config_right_issues_deprecation_warning(self, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        deprecation_warning = "DeprecationWarning: alembic_config_right is deprecated."
        assert deprecation_warning in result.stdout.str()


class TestNewDbLeft:
    @pytest.fixture(autouse=True)
    def create_test_file(self, pytester):
        pytester.makepyfile(
            """
            def test_new_db(new_db_left):
                pass
            """
        )

    def test_new_db_left(self, drop_database_mock, create_database_mock, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        assert create_database_mock.call_args_list == [call("left")]
        assert drop_database_mock.call_args_list == [call("left")]

    @pytest.mark.usefixtures("drop_database_mock", "create_database_mock")
    def test_new_db_left_issues_deprecation_warning(self, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        deprecation_warning = "DeprecationWarning: new_db_left is deprecated."
        assert deprecation_warning in result.stdout.str()


class TestNewDbRight:
    @pytest.fixture(autouse=True)
    def create_test_file(self, pytester):
        pytester.makepyfile(
            """
            def test_new_db(new_db_right):
                pass
            """
        )

    def test_new_db_right(self, drop_database_mock, create_database_mock, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        assert create_database_mock.call_args_list == [call("right")]
        assert drop_database_mock.call_args_list == [call("right")]

    @pytest.mark.usefixtures("drop_database_mock", "create_database_mock")
    def test_new_db_right_issues_deprecation_warning(self, pytester):
        result = pytester.runpytest()
        assert result.ret == 0

        deprecation_warning = "DeprecationWarning: new_db_right is deprecated."
        assert deprecation_warning in result.stdout.str()

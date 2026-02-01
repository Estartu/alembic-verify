from unittest.mock import MagicMock, Mock, call, patch

import pytest

from alembicverify.util import (
    _get_revision,
    get_current_revision,
    get_head_revision,
    make_alembic_config,
    prepare_schema_from_migrations,
)


def test_make_alembic_config():
    config = make_alembic_config("sqlite:///:memory:", "/some/path")

    assert config.get_main_option("script_location") == "/some/path"
    assert config.get_main_option("sqlalchemy.url") == "sqlite:///:memory:"


class TestPrepareSchemaFromMigrations:
    @pytest.fixture
    def create_engine_mock(self):
        with patch("alembicverify.util.create_engine") as m:
            yield m

    @pytest.fixture
    def Config_mock(self):
        with patch("alembicverify.util.Config") as m:
            yield m

    @pytest.fixture
    def script_directory_mock(self):
        with patch("alembicverify.util.ScriptDirectory") as m:
            yield m

    @pytest.fixture
    def command_mock(self):
        with patch("alembicverify.util.command") as m:
            yield m

    def test_called_as_function_with_default_revision_value(
        self, Config_mock, create_engine_mock, script_directory_mock, command_mock
    ):
        uri = "Migrations URI"
        config = Config_mock()

        engine, script = prepare_schema_from_migrations(uri, config)

        assert create_engine_mock.return_value == engine
        assert script_directory_mock.from_config.return_value == script

        create_engine_mock.assert_called_once_with(uri)
        script_directory_mock.from_config.assert_called_once_with(config)
        command_mock.upgrade.assert_called_once_with(config, "head")

        # test that the engine is not disposed automatically
        assert engine.dispose.call_count == 0

    def test_called_as_function_with_custom_revision_value(
        self, Config_mock, create_engine_mock, script_directory_mock, command_mock
    ):
        uri = "Migrations URI"
        config = Config_mock()

        engine, script = prepare_schema_from_migrations(uri, config, revision="some revision")

        assert create_engine_mock.return_value == engine
        assert script_directory_mock.from_config.return_value == script

        create_engine_mock.assert_called_once_with(uri)
        script_directory_mock.from_config.assert_called_once_with(config)
        command_mock.upgrade.assert_called_once_with(config, "some revision")

        # test that the engine is not disposed automatically
        assert engine.dispose.call_count == 0

    def test_called_as_context_manager_with_default_revision_value(
        self, Config_mock, create_engine_mock, script_directory_mock, command_mock
    ):
        uri = "Migrations URI"
        config = Config_mock()

        with prepare_schema_from_migrations(uri, config) as (engine, script):
            assert engine is not None
            assert script is not None
            assert engine.dispose.call_count == 0
            assert script_directory_mock.from_config.call_count == 1
            assert command_mock.upgrade.call_args_list == [call(config, "head")]

        # test that after the context manager exits, the engine is disposed
        assert engine.dispose.call_count == 1
        create_engine_mock.assert_called_once_with(uri)

    def test_called_as_context_manager_with_custom_revision_value(
        self, Config_mock, create_engine_mock, script_directory_mock, command_mock
    ):
        uri = "Migrations URI"
        config = Config_mock()

        with prepare_schema_from_migrations(uri, config, revision="some revision") as (
            engine,
            script,
        ):
            assert engine is not None
            assert script is not None
            assert engine.dispose.call_count == 0
            assert script_directory_mock.from_config.call_count == 1
            assert command_mock.upgrade.call_args_list == [call(config, "some revision")]

        # test that after the context manager exits, the engine is disposed
        assert engine.dispose.call_count == 1
        create_engine_mock.assert_called_once_with(uri)


class TestGetRevision:
    @pytest.fixture
    def _get_revision_mock(self):
        with patch("alembicverify.util._get_revision") as m:
            yield m

    def test_get_current_revision(self, _get_revision_mock):
        config, engine, script = Mock(), Mock(), Mock()

        result = get_current_revision(config, engine, script)

        assert _get_revision_mock.return_value == result
        _get_revision_mock.assert_called_once_with(config, engine, script, revision_type="current")

    def test_get_head_revision(self, _get_revision_mock):
        config, engine, script = Mock(), Mock(), Mock()

        result = get_head_revision(config, engine, script)

        assert _get_revision_mock.return_value == result
        _get_revision_mock.assert_called_once_with(config, engine, script, revision_type="head")


class TestGetRevisionHelper:
    @pytest.fixture
    def EnvironmentContext_mock(self):
        with patch("alembicverify.util.EnvironmentContext") as m:
            yield m

    def test__get_revision_with_head(self, EnvironmentContext_mock):
        config, engine, script = Mock(), MagicMock(), Mock()

        revision = _get_revision(config, engine, script, revision_type="head")

        engine.connect.assert_called_once_with()
        EnvironmentContext_mock.assert_called_once_with(config, script)

        env_context = EnvironmentContext_mock().__enter__.return_value
        conn = engine.connect().__enter__.return_value

        env_context.configure.assert_called_once_with(conn, version_table="alembic_version")

        env_context.get_head_revision.assert_called_once_with()

        assert env_context.get_head_revision.return_value == revision

    def test__get_revision_with_current(self, EnvironmentContext_mock):
        config, engine, script = Mock(), MagicMock(), Mock()

        revision = _get_revision(config, engine, script, revision_type="current")

        engine.connect.assert_called_once_with()
        EnvironmentContext_mock.assert_called_once_with(config, script)

        env_context = EnvironmentContext_mock().__enter__.return_value
        conn = engine.connect().__enter__.return_value

        env_context.configure.assert_called_once_with(conn, version_table="alembic_version")

        env_context.get_context.assert_called_once_with()

        migration_context = env_context.get_context.return_value

        assert migration_context.get_current_revision.return_value == revision

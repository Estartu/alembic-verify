def pytest_addoption(parser):
    """Add command line options for the database connection."""
    parser.addoption("--db-user", action="store", default=None, help="Database user")
    parser.addoption("--db-password", action="store", default=None, help="Database password")
    parser.addoption("--db-host", action="store", default=None, help="Database host")
    parser.addoption("--db-port", action="store", default=None, help="Database port")

import pytest
import time

from .test_utils import *


def pytest_addoption(parser):
    parser.addoption(
        "--longrun",
        action="store_true",
        dest="longrun",
        default=False,
        help="enable longrun decorated tests",
    )


def pytest_configure(config):
    if not config.option.longrun:
        setattr(config.option, "markexpr", "not longrun")


@pytest.fixture(scope="function")
def config():
    return copy.deepcopy(TEST_WH_CONFIG)


@pytest.fixture(scope="function")
def ds_config():
    config = copy.deepcopy(TEST_WH_CONFIG)
    return config["datasources"]["testdb1"]


@pytest.fixture(scope="function")
def adhoc_config():
    return copy.deepcopy(TEST_ADHOC_CONFIG)


@pytest.fixture(scope="function")
def wh(config):
    return Warehouse(config=config)


@pytest.fixture(scope="function")
def saved_wh():
    name = "test_warehouse_%s" % time.time()
    config_url = REMOTE_CONFIG_URL
    wh = Warehouse(config=config_url)
    wh_id = wh.save(name, config_url, meta=dict(test=1))
    yield wh
    try:
        Warehouse.delete(wh_id)
    except:
        pass


@pytest.fixture(scope="function")
def adhoc_ds(config):
    return get_adhoc_datasource()


@pytest.fixture(scope="function")
def mysql_ds_config():
    return load_datasource_config("test_mysql_ds_config.json")


@pytest.fixture(scope="function")
def mysql_ds(mysql_ds_config):
    return DataSource("mysql", config=mysql_ds_config)


@pytest.fixture(scope="function")
def mysql_wh(mysql_ds):
    return Warehouse(datasources=[mysql_ds])


@pytest.fixture(scope="function")
def postgresql_ds_config():
    return load_datasource_config("test_postgresql_ds_config.json")


@pytest.fixture(scope="function")
def postgresql_ds(postgresql_ds_config):
    return DataSource("postgresql", config=postgresql_ds_config)


@pytest.fixture(scope="function")
def postgresql_wh(postgresql_ds):
    return Warehouse(datasources=[postgresql_ds])


@pytest.fixture
def pymysql_conn():
    conn = get_pymysql_conn()
    yield conn
    try:
        conn.close()
    except:
        pass


@pytest.fixture
def sqlalchemy_conn():
    conn = get_sqlalchemy_conn()
    yield conn
    try:
        conn.close()
    except:
        pass

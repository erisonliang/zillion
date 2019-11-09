import copy
import contextlib
import cProfile
import pstats
import time

import climax
from tlbx import dbg, st, Script, Arg

from zillion.configs import load_warehouse_config
from zillion.core import TableTypes
from zillion.warehouse import DataSource, AdHocDataSource, Warehouse
from test_utils import TestBase, run_tests, create_adhoc_datatable, get_testdb_url

TEST_CONFIG = load_warehouse_config("test_config.json")


@contextlib.contextmanager
def profiled(pattern=None):
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats("cumulative")
    dbg("Top 10 calls by cumulative time:")
    stats.print_stats(10)
    if pattern:
        stats.sort_stats("time")
        dbg("Top 10 %s calls by function time:" % pattern)
        stats.print_stats(pattern, 10)


def init_datasources():
    ds1 = DataSource("testdb1", get_testdb_url(), reflect=True)
    return [ds1]


def get_adhoc_ds(size):
    facts = ["adhoc_fact1", "adhoc_fact2", "adhoc_fact3", "adhoc_fact4"]
    dimensions = ["partner_name", "campaign_name", "lead_id"]

    column_defs = {
        "partner_name": {"fields": ["partner_name"], "type": str},
        "campaign_name": {"fields": ["campaign_name"], "type": str},
        "lead_id": {"fields": ["lead_id"], "type": int},
        "adhoc_fact1": {"fields": ["adhoc_fact1"], "type": float},
        "adhoc_fact2": {"fields": ["adhoc_fact2"], "type": float},
        "adhoc_fact3": {"fields": ["adhoc_fact3"], "type": float},
        "adhoc_fact4": {"fields": ["adhoc_fact4"], "type": float},
    }

    start = time.time()
    dt = create_adhoc_datatable(
        "adhoc_table1", TableTypes.FACT, column_defs, ["partner_name"], size
    )
    adhoc_ds = AdHocDataSource([dt])
    dbg("Created AdHocDataSource in %.3fs" % (time.time() - start))
    return facts, dimensions, adhoc_ds


class TestZillionPerformance(TestBase):
    def setUp(self):
        self.datasources = init_datasources()
        self.config = copy.deepcopy(TEST_CONFIG)

    def tearDown(self):
        del self.datasources
        self.config = None

    def testPerformance(self):
        wh = Warehouse(self.datasources, config=self.config)
        facts, dimensions, adhoc_ds = get_adhoc_ds(1e5)
        with profiled("zillion"):
            result = wh.report(
                facts, dimensions=dimensions, adhoc_datasources=[adhoc_ds]
            )
        self.assertTrue(result)

    def testPerformanceMultiRollup(self):
        wh = Warehouse(self.datasources, config=self.config)
        facts, dimensions, adhoc_ds = get_adhoc_ds(1e5)
        rollup = 2
        with profiled("zillion"):
            result = wh.report(
                facts,
                dimensions=dimensions,
                rollup=rollup,
                adhoc_datasources=[adhoc_ds],
            )
        self.assertTrue(result)


@Script(
    Arg("testnames", type=str, nargs="*", help="Names of tests to run"),
    Arg("--debug", action="store_true"),
)
def main(testnames, debug):
    run_tests(TestZillionPerformance, testnames, debug)


if __name__ == "__main__":
    main()

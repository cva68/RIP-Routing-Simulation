# Ignore this file from flake8 - behave is not compliant by design
# flake8: noqa

from behave import *
from ripd.ripd import RIPDaemon
import time
import threading


@given('no routers are running')
def step_no_routers(context):
    """
        Ensure no routers are running
    """
    if hasattr(context, 'routers'):
        for router in context.routers.values():
            router._run = False
    if hasattr(context, 'router_threads'):
        for thread in context.router_threads.values():
            thread.join(timeout=5)
    time.sleep(2) # Allow port close to propogate


@given('router {n:d} is running')
def step_no_routers(context, n):
    """
        Ensure a router n is running
    """
    assert hasattr(context, 'routers')
    assert n in context.routers.keys()


@when('router {n:d} is started')
def step_start_router(context, n):
    """
    Start router n in a separate thread.
    """
    if not hasattr(context, 'routers'):
        context.routers = {}
    if not hasattr(context, 'router_threads'):
        context.router_threads = {}

    router = RIPDaemon(f"config/{n}.ini")
    context.routers[n] = router

    # Now start it in a thread
    thread = threading.Thread(target=router.start, daemon=True)
    thread.start()
    context.router_threads[n] = thread


@when('router {n:d} is killed')
def step_start_router(context, n):
    """
        Kill the thread of router n
    """
    assert hasattr(context, 'routers')
    assert hasattr(context, 'router_threads')

    context.routers[n]._run = False

    # Wait for the thread to finish
    if n in context.router_threads:
        context.router_threads[n].join(timeout=5)


@given('the following routers have started')
def step_start_multiple_routers(context):
    """
    Start multiple routers as listed in the table.
    """
    if not hasattr(context, 'routers'):
        context.routers = {}
    if not hasattr(context, 'router_threads'):
        context.router_threads = {}

    for row in context.table:
        n = int(row['router'])
        router = RIPDaemon(f"config/{n}.ini")
        context.routers[n] = router

        # Now start it in a thread
        thread = threading.Thread(target=router.start, daemon=True)
        thread.start()
        context.router_threads[n] = thread


@when('we wait for {n:d} seconds')
def step_wait(context, n):
    time.sleep(n)


@then('the routing tables should contain')
def step_check_routing_tables(context):
    """
    Check that the routing tables contain the expected entries.
    """
    for row in context.table:
        router_id = int(row['router'])
        destination_id = int(row['destination'])
        expected_metric = int(row['metric'])

        assert router_id in context.routers, f"Router {router_id} not found."

        router = context.routers[router_id]
        table = router._table

        entry = table.get_entry(destination_id)
        assert entry is not None, f"No route to {destination_id} in router {router_id}'s table."
        assert entry.metric == expected_metric, (
            f"Expected metric {expected_metric} for route to {destination_id} in router {router_id}, got {entry.metric}"
        )


@then('the routing table of router {n:d} contains a route to {m:d} with metric {metric:d}')
def step_check_entry_metric(context, n, m, metric):
    assert n in context.routers.keys()
    assert m in context.routers.keys()
    table = context.routers[n]._table
    print(context)
    print(table)
    assert table.get_entry(m).metric == metric


@then('the routing table of router {n:d} contains a route to {m:d} with a timeout greater than {timeout:d}')
def step_check_entry_timeout(context, n, m, timeout):
    assert n in context.routers.keys()
    assert m in context.routers.keys()
    table = context.routers[n]._table
    assert table.get_entry(m).timeout >= timeout


@then('the routing table of router {n:d} contains a route to {m:d} with a garbage collection timer running')
def step_check_entry_garbage(context, n, m):
    assert n in context.routers.keys()
    assert m in context.routers.keys()
    table = context.routers[n]._table
    assert table.get_entry(m).garbage_collection_timer


@then('the routing table of router {n:d} does not contain a route to {m:d}')
def step_check_no_route(context, n, m):
    assert n in context.routers.keys()
    table = context.routers[n]._table
    assert table.get_entry(m) is None
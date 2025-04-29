"""
    RIPDaemon - Behave environment functions.
    MIT License. Copyright © 2025 Connor Varney, Kahu Jones
"""


# Ensure routers are stopped at the end of each scenario
def after_scenario(context, scenario):
    if hasattr(context, 'routers'):
        for router in context.routers.values():
            router._run = False

    if hasattr(context, 'router_threads'):
        for thread in context.router_threads.values():
            thread.join(timeout=5)

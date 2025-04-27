def after_scenario(context, scenario):
    if hasattr(context, 'routers'):
        for router in context.routers.values():
            router._run = False

    if hasattr(context, 'router_threads'):
        for thread in context.router_threads.values():
            thread.join(timeout=5)

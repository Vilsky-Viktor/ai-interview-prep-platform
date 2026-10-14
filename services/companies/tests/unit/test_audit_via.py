import importlib
import inspect
import pkgutil

from fastapi.routing import APIRoute

import app.routers


def routes() -> list[APIRoute]:
    found = []

    for module in pkgutil.iter_modules(app.routers.__path__):
        router = getattr(importlib.import_module(f"app.routers.{module.name}"), "router", None)

        if router is not None:
            found += [route for route in router.routes if isinstance(route, APIRoute)]

    return found


def test_every_audited_route_records_what_it_came_through():
    """An action through the in-app assistant or an AI app shows as such in the oversight log,
    not as one done in the app: every route that writes the log takes `via`."""
    audited = [route for route in routes() if "audit.record(" in inspect.getsource(route.endpoint)]

    assert len(audited) >= 7
    for route in audited:
        assert "via" in inspect.signature(route.endpoint).parameters, route.path

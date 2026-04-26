import pytest


def _has_minizinc_runtime() -> bool:
    try:
        import minizinc

        return minizinc.default_driver is not None
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if (_has_minizinc_runtime()):
        return

    skip_integration = pytest.mark.skip(reason="MiniZinc runtime not available")
    for item in items:
        if ("integration" in item.keywords):
            item.add_marker(skip_integration)

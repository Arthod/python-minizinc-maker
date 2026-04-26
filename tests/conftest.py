import pytest
import shutil

from tests.mzn_verifier import verify_mzn_text


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


@pytest.fixture(autouse=True)
def verify_rendered_mzn_models(monkeypatch, request):
    # Keep local/unit workflow fast when CLI is unavailable.
    if (shutil.which("minizinc") is None):
        yield
        return

    if (request.node.get_closest_marker("no_mzn_verify") is not None):
        yield
        return

    import pymzm

    original_render = pymzm.Model._render_model_string
    rendered_models = []

    def _wrapped_render(self, *args, **kwargs):
        rendered = original_render(self, *args, **kwargs)
        rendered_models.append(rendered)
        return rendered

    monkeypatch.setattr(pymzm.Model, "_render_model_string", _wrapped_render)
    yield

    seen = set()
    for rendered in rendered_models:
        if (rendered in seen):
            continue
        seen.add(rendered)

        ok, message = verify_mzn_text(rendered)
        if (not ok):
            pytest.fail(f"Generated invalid MiniZinc model:\n{message}\n\nModel:\n{rendered}")

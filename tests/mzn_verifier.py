import shutil
import subprocess
import tempfile
from pathlib import Path


def _minizinc_cli_path():
    return shutil.which("minizinc")


def _verify_with_minizinc_cli(model_path: Path):
    cli = _minizinc_cli_path()
    if (cli is None):
        return False, "MiniZinc CLI not found"

    # Prefer explicit model-check mode and fall back to legacy spellings when unavailable.
    candidate_args = [
        ["--model-check-only", str(model_path)],
        ["--check-only", str(model_path)],
    ]

    last_error = ""
    for args in candidate_args:
        proc = subprocess.run(
            [cli, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if (proc.returncode == 0):
            return True, ""

        stderr = (proc.stderr or "").strip().lower()
        if ("unknown option" in stderr or "unrecognized option" in stderr):
            last_error = proc.stderr or proc.stdout
            continue

        return False, (proc.stderr or proc.stdout or "MiniZinc verification failed")

    return False, (last_error or "MiniZinc verification failed")


def assert_valid_mzn_or_skip(testcase, mzn_text: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "model.mzn"
        model_path.write_text(mzn_text, encoding="utf-8")

        ok, message = _verify_with_minizinc_cli(model_path)
        if (not ok and "cli not found" in message.lower()):
            testcase.skipTest(message)
        testcase.assertTrue(ok, msg=message)

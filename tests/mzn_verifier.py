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

    proc = subprocess.run(
        [cli, "--model-check-only", str(model_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if (proc.returncode == 0):
        return True, ""

    return False, (proc.stderr or proc.stdout or "MiniZinc verification failed")


def verify_mzn_text(mzn_text: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "pymzm_verify_input.mzn"
        model_path.write_text(mzn_text, encoding="utf-8")
        return _verify_with_minizinc_cli(model_path)


def assert_valid_mzn(testcase, mzn_text: str):
    ok, message = verify_mzn_text(mzn_text)
    if (not ok and "cli not found" in message.lower()):
        testcase.skipTest(message)
    testcase.assertTrue(ok, msg=message)

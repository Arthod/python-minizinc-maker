from pathlib import Path
import sys

import pytest


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    if (str(repo_root) not in sys.path):
        sys.path.insert(0, str(repo_root))

    raise SystemExit(pytest.main([str(Path(__file__).resolve().parent)]))
# Test Matrix

This matrix defines the baseline regression structure for the project.

## Goals

- Keep fast unit feedback independent of local MiniZinc installation.
- Keep integration coverage for solver-backed behavior.
- Keep deterministic rendering guarded by snapshot-style assertions.
- Leave room for property-style equivalence tests as language coverage grows.

## Categories

| Category | Purpose | Current coverage | Marker |
|---|---|---|---|
| Unit | Expression/model/serializer behavior without solver runtime dependency | `tests/test_model_execution.py`, `tests/test_architecture.py`, `tests/test_deterministic_generation.py`, `tests/test_expression_validation.py` | `unit` |
| Integration | End-to-end behavior that requires MiniZinc solver runtime | `tests/test_expression.py`, `tests/test_examples.py`, `tests/test_misc.py` | `integration` |
| Snapshot | Deterministic generated MiniZinc text | `tests/test_deterministic_generation.py` | `snapshot` |
| Property | Expression equivalence style checks | `tests/test_expression.py` (current approximation) | `property` |

## Commands

Run unit baseline:

```bash
python -m pytest -m unit -q
```

Run integration suite:

```bash
python -m pytest -m integration -q
```

Run deterministic snapshot suite:

```bash
python -m pytest -m snapshot -q
```

Run property-style suite:

```bash
python -m pytest -m property -q
```

Run all tests:

```bash
python -m pytest -q
```

## Runtime behavior without MiniZinc

`tests/conftest.py` skips tests marked `integration` when MiniZinc runtime is unavailable. This keeps local and CI unit validation reliable on hosts without solver installation.

## Deterministic Solver Utilities

Use `tests/solver_utils.py` for stable integration solve defaults.

- `lookup_default_solver()`
- `deterministic_solver_config(...)`
- `deterministic_instance_solve(...)`

These utilities centralize deterministic defaults (`random_seed=1`, `threads=1`) to reduce test flakiness when integration tests run with a solver runtime.

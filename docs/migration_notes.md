# Migration Notes

This file tracks user-facing API changes that may require updates in downstream code.

## 2026-04-26

### Execution and Solver API

- Added `SolverConfig` and `Model.solve_with(config)`.
- `Model.solve(...)` still supports classic keyword arguments.

Before:
```python
result = model.solve(solver="gecode", timeout=10, threads=4)
```

After (optional structured form):
```python
config = pymzm.SolverConfig(solver="gecode", timeout=10, threads=4)
result = model.solve_with(config)
```

### Solution Enumeration Path

- Removed dedicated `solve_all` convenience path.
- Use `model.solve(all_solutions=True)` for all-solution enumeration.

Before:
```python
results = model.solve_all(...)
```

After:
```python
results = model.solve(..., all_solutions=True)
```

### Solve Result Normalization

- `Model.solve(...)` returns normalized `SolveResult`.
- Existing access patterns remain supported for common use:
  - `result["x"]`
  - `result.x`
  - `result[0].x` for all-solution cases

Before:
```python
result = model.solve(...)
status = result.status
```

After:
```python
result = model.solve(...)
status = result.status
status_code = result.status_code  # SAT, OPTIMAL, UNSAT, UNKNOWN, ERROR
```

### Model Compilation State

- `Model.generate()` now synchronizes compiled state without accumulating repeated hidden model text.
- Repeated calls with unchanged model content are idempotent.

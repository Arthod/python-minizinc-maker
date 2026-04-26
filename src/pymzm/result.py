from enum import Enum
from typing import Any


_STATUS_MAP = {
    "SATISFIED": "SAT",
    "ALL_SOLUTIONS": "SAT",
    "OPTIMAL_SOLUTION": "OPTIMAL",
    "UNSATISFIABLE": "UNSAT",
    "UNKNOWN": "UNKNOWN",
    "ERROR": "ERROR",
    "UNBOUNDED": "SAT",
}


class SolutionView:
    def __init__(self, solution: Any):
        self._raw_solution = solution
        self._data = self._extract_solution_data(solution)

    @property
    def raw_solution(self):
        return self._raw_solution

    @staticmethod
    def _extract_solution_data(solution: Any) -> dict[str, Any]:
        if solution is None:
            return {}
        if isinstance(solution, dict):
            return {k: SolutionView._decode_value(v) for k, v in solution.items()}
        if hasattr(solution, "__dict__"):
            raw = vars(solution)
            return {k: SolutionView._decode_value(v) for k, v in raw.items()}
        raise TypeError("Unsupported solution object type for normalized access.")

    @staticmethod
    def _decode_value(value: Any):
        if isinstance(value, Enum):
            return value.name
        if isinstance(value, (bool, int, float, str, type(None))):
            return value
        if isinstance(value, (set, frozenset)):
            return {SolutionView._decode_value(v) for v in value}
        if isinstance(value, tuple):
            return tuple(SolutionView._decode_value(v) for v in value)
        if isinstance(value, list):
            return [SolutionView._decode_value(v) for v in value]
        if isinstance(value, dict):
            return {k: SolutionView._decode_value(v) for k, v in value.items()}
        if hasattr(value, "tolist"):
            return SolutionView._decode_value(value.tolist())
        return value

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __getitem__(self, key: str):
        return self._data[key]

    def __getattr__(self, name: str):
        if name in self._data:
            return self._data[name]
        raise AttributeError(name)

    def __contains__(self, key: str) -> bool:
        return key in self._data


class SolveResult:
    def __init__(self, raw_result):
        self.raw_result = raw_result
        self.status = getattr(raw_result, "status", None)
        self.statistics = getattr(raw_result, "statistics", None)
        self.solution = self._extract_solution_container(raw_result)
        self.solutions = self._normalize_solutions(self.solution)
        self.status_code = self._normalize_status_code(self.status)

    @staticmethod
    def _extract_solution_container(raw_result):
        return getattr(raw_result, "solution", None)

    @staticmethod
    def _normalize_solutions(solution_container):
        if solution_container is None:
            return []
        if isinstance(solution_container, (list, tuple)):
            return [SolutionView(solution) for solution in solution_container]
        return [SolutionView(solution_container)]

    @staticmethod
    def _normalize_status_code(status) -> str:
        if status is None:
            return "UNKNOWN"
        status_name = getattr(status, "name", str(status)).upper()
        return _STATUS_MAP.get(status_name, status_name)

    @property
    def raw_statistics(self):
        return self.statistics

    @property
    def has_solution(self) -> bool:
        return len(self.solutions) > 0

    @property
    def is_sat(self) -> bool:
        return self.status_code in {"SAT", "OPTIMAL"}

    @property
    def is_unsat(self) -> bool:
        return self.status_code == "UNSAT"

    @property
    def is_unknown(self) -> bool:
        return self.status_code == "UNKNOWN"

    @property
    def is_error(self) -> bool:
        return self.status_code == "ERROR"

    @property
    def is_optimal(self) -> bool:
        return self.status_code == "OPTIMAL"

    def to_dict(self) -> dict[str, Any]:
        if not self.solutions:
            return {}
        return self.solutions[0].to_dict()

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.solutions[key]
        if isinstance(key, slice):
            return self.solutions[key]
        if not self.solutions:
            raise KeyError(key)
        return self.solutions[0][key]

    def __getattr__(self, name: str):
        if self.solutions and name in self.solutions[0]:
            return self.solutions[0][name]
        raise AttributeError(name)

    def __len__(self) -> int:
        return len(self.solutions)

    def __iter__(self):
        return iter(self.solutions)

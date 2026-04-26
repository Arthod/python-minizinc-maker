from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class SolveIR:
    criteria: str
    expression: Optional[str] = None
    method: Optional[str] = None
    restart_strategy: Optional[str] = None
    annotations: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelIR:
    includes: Tuple[str, ...]
    declarations: Tuple[str, ...]
    constraints: Tuple[str, ...]
    solve: SolveIR
    function_declarations: Tuple[str, ...] = ()
    predicate_declarations: Tuple[str, ...] = ()

from .base import BackendAdapter
from ..ir import ModelIR


class MznTextBackend(BackendAdapter):
    """Deterministic MiniZinc text serializer for ModelIR."""

    def render_model(self, model_ir: ModelIR) -> str:
        lines = []

        for include_file in model_ir.includes:
            lines.append(f'include "{include_file}";')

        lines.extend(model_ir.declarations)
        lines.extend(model_ir.constraints)

        solve = model_ir.solve
        solve_text = ""
        if solve.method is not None:
            solve_text += f":: {solve.method}\\n"
            if solve.restart_strategy is not None:
                solve_text += f"      :: {solve.restart_strategy}\\n "

        solve_text += solve.criteria
        if solve.expression is not None:
            solve_text += f" {solve.expression}"

        lines.append(f"solve {solve_text};")
        return "\\n".join(lines) + "\\n"

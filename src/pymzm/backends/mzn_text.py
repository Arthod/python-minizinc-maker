from .base import BackendAdapter
from ..ir import ModelIR


class MznTextBackend(BackendAdapter):
    """Deterministic MiniZinc text serializer for ModelIR."""

    def render_model(self, model_ir: ModelIR) -> str:
        lines = []

        for include_file in model_ir.includes:
            lines.append(f'include "{include_file}";')

        lines.extend(model_ir.declarations)
        lines.extend(model_ir.function_declarations)
        lines.extend(model_ir.predicate_declarations)
        lines.extend(model_ir.constraints)

        solve = model_ir.solve
        solve_annotations = []
        if solve.method is not None:
            solve_annotations.append(solve.method)
        if solve.restart_strategy is not None:
            solve_annotations.append(solve.restart_strategy)
        solve_annotations.extend(solve.annotations)

        solve_text = ""
        if len(solve_annotations):
            solve_text += " ".join(f":: {annotation}" for annotation in solve_annotations)
            solve_text += " "

        solve_text += solve.criteria
        if solve.expression is not None:
            solve_text += f" {solve.expression}"

        lines.append(f"solve {solve_text};")
        lines.extend(model_ir.output_items)
        return "\n".join(lines) + "\n"

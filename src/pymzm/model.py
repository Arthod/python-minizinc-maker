
import minizinc
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, Union

from .exceptions import *
from .variable import *
from .constraint import *
from .expression import *
from .constant import *
from .ir import ModelIR, SolveIR
from .backends import MznTextBackend
from .result import SolveResult

SOLVE_MAXIMIZE = "maximize"
SOLVE_MINIMIZE = "minimize"
SOLVE_SATISFY = "satisfy"


class EnumValue(Expression):
    def __init__(self, enum_type_name: str, token: str):
        self.enum_type_name = enum_type_name
        self.token = token
        super().__init__(token)

    def _to_mz_token(self):
        return self.token


class EnumDomain:
    def __init__(self, type_name: str, members: List[str]):
        self.type_name = type_name
        self.members = tuple(members)
        self._member_values = {
            member: EnumValue(type_name, member)
            for member in self.members
        }

    def __getitem__(self, member: str) -> EnumValue:
        return self._member_values[member]

    def __iter__(self):
        for member in self.members:
            yield self._member_values[member]

    def __contains__(self, member: str) -> bool:
        return member in self._member_values

    def __getattr__(self, member: str) -> EnumValue:
        if (member in self._member_values):
            return self._member_values[member]
        raise AttributeError(member)

    def to_declaration(self) -> str:
        return f"enum {self.type_name} = {{{', '.join(self.members)}}};"


@dataclass(frozen=True)
class SolverConfig:
    solver: Union[str, Any] = "gecode"
    timeout: Any = None
    random_seed: Optional[int] = None
    threads: Optional[int] = None
    free_search: bool = False
    all_solutions: bool = False
    extra_solve_args: dict[str, Any] = field(default_factory=dict)

    def with_updates(self, **overrides):
        values = {
            "solver": self.solver,
            "timeout": self.timeout,
            "random_seed": self.random_seed,
            "threads": self.threads,
            "free_search": self.free_search,
            "all_solutions": self.all_solutions,
            "extra_solve_args": dict(self.extra_solve_args),
        }
        values.update(overrides)
        return SolverConfig(**values)

class RestartStrategy:
    def __init__(self, restart_type: str, scale: int):
        self.restart_type = restart_type
        self.scale = scale

    def __str__(self):
        return f"{self.restart_type}({self.scale})"

class RestartConstant(RestartStrategy):
    def __init__(self, scale):
        super().__init__("restart_constant", scale)

class RestartLinear(RestartStrategy):
    def __init__(self, scale):
        super().__init__("restart_linear", scale)

class RestartGeometric(RestartStrategy):
    def __init__(self, base, scale):
        self.base = base
        super().__init__("restart_geometric", scale)

    def __str__(self):
        return f"{self.restart_type}({self.base}, {self.scale})"

class RestartLuby(RestartStrategy):
    def __init__(self, scale):
        super().__init__("restart_luby", scale)


class RestartNone(RestartStrategy):
    def __init__(self):
        super().__init__("restart_none", 0)

    def __str__(self):
        return self.restart_type



class SeqSearch:
    def __init__(self, search_annotations: list["SearchAnnotation"]):
        self.search_annotations = search_annotations
        if (not all(isinstance(sa, SearchAnnotation) for sa in search_annotations)):
            raise PymzmInvalidSearchAnnotation()
        
    def __str__(self):
        return f"seq_search([{','.join(str(sa) for sa in self.search_annotations)}])"

class SearchAnnotation:
    def __init__(self, search_type: str, variables: List["Variable"], varchoice: str, valchoice: str):
        self.search_type = search_type
        self.variables = variables

        self.varchoice = varchoice
        if (not self.varchoice in AnnotationVariableChoice.VARCHOICES):
            raise PymzmInvalidVarchoiceAnnotation("varchoice")
        
        self.valchoice = valchoice
        if (not self.valchoice in AnnotationValueChoice.VALCHOICES):
            raise PymzmInvalidValchoiceAnnotation("valchoice")
        
    def __str__(self):
        return f"{self.search_type}({self.variables}, {self.varchoice}, {self.valchoice})"

class IntSearch(SearchAnnotation):
    def __init__(self, variables: List["Variable"], varchoice: str, valchoice: str):
        if (not all(isinstance(v, Variable) for v in variables)):
            raise PymzmInvalidVariableError("variables", "Atleast one variable is not an integer.")
        
        super().__init__("int_search", variables, varchoice, valchoice)

class BoolSearch(SearchAnnotation):
    def __init__(self, variables: List["VariableBool"], varchoice: str, valchoice: str):
        if (not all(isinstance(v, VariableBool) for v in variables)):
            raise PymzmInvalidVariableError("variables", "Atleast one variable is not a bool.")
        
        super().__init__("bool_search", variables, varchoice, valchoice)

class SetSearch(SearchAnnotation):
    def __init__(self, variables: List["Expression"], varchoice: str, valchoice: str):
        if (not all(isinstance(v, Variable) or not all(v.vtype == Variable.VTYPE_SET) for v in variables)):
            raise PymzmInvalidVariableError("variables", "Atleast one variable is not a set.")
        
        super().__init__("set_search", variables, varchoice, valchoice)

class FloatSearch(SearchAnnotation):
    def __init__(self, variables: List["Expression"], precision: float, varchoice: str, valchoice: str):
        raise NotImplementedError()
    
class AnnotationVariableChoice:
    VARCHOICES = [
        VARCHOICE_INPUT_ORDER, # Choose variables in the order they appear in vars.
        VARCHOICE_FIRST_FAIL, # Choose the variable with the smallest domain.
        VARCHOICE_ANTI_FIRST_FAIL, # Choose the variable with the largest domain
        VARCHOICE_SMALLEST, #Choose the variable with the smallest value in its domain.
        VARCHOICE_LARGEST, #Choose the variable with the largest value in its domain.
        VARCHOICE_OCCURRENCE, # Choose the variable with the largest number of attached constraints.
        VARCHOICE_MOST_CONSTRAINED, # Choose the variable with the smallest domain, breaking ties using the number of constraints.
        VARCHOICE_MAX_REGRET, # Choose the variable with the largest difference between the two smallest values in its domain.
        VARCHOICE_DOM_W_DEG, # Choose the variable with the smallest value of domain size divided by weighted degree, where the weighted degree is the number of times the variables been in a constraint which failed
        VARCHOICE_IMPACT, # Choose the variable with the highest impact during search.
    ] = [
        "input_order",
        "first_fail",
        "anti_first_fail",
        "smallest",
        "largest",
        "occurrence",
        "most_constrained",
        "max_regret",
        "dom_w_deg",
        "impact",
    ]

class AnnotationValueChoice:
    VALCHOICES = [
        VALCHOICE_INDOMAIN_MIN, # Assign the smallest value in the variable’s domain.
        VALCHOICE_INDOMAIN_MAX, # Assign the largest value in the variable’s domain.
        VALCHOICE_INDOMAIN_MIDDLE, # Assign the value in the variable’s domain closest to the mean of its current bounds.
        VALCHOICE_INDOMAIN_MEDIAN, # Assign the middle value in the variable’s domain.
        VALCHOICE_INDOMAIN, # Nondeterministically assign values to the variable in ascending order.
        VALCHOICE_INDOMAIN_RANDOM, # Assign a random value from the variable’s domain.
        VALCHOICE_INDOMAIN_SPLIT, # Bisect the variable’s domain, excluding the upper half first.
        VALCHOICE_INDOMAIN_REVERSE_SPLIT, # Bisect the variable’s domain, excluding the lower half first.
        VALCHOICE_INDOMAIN_INTERVAL, # If the variable’s domain consists of several contiguous intervals, reduce the domain to the first interval. Otherwise just split the variable’s domain.
        VALCHOICE_INDOMAIN_SPLIT_RANDOM, # Bisect the variable's domain and randomly choose the side to exclude first.
        VALCHOICE_OUTDOMAIN_MIN, # Exclude the smallest value from the variable's domain.
        VALCHOICE_OUTDOMAIN_MAX, # Exclude the largest value from the variable's domain.
        VALCHOICE_OUTDOMAIN_MEDIAN, # Exclude the middle value from the variable's domain.
        VALCHOICE_OUTDOMAIN_RANDOM, # Exclude a random value from the variable's domain.
    ] = [
        "indomain_min",
        "indomain_max",
        "indomain_middle",
        "indomain_median",
        "indomain",
        "indomain_random",
        "indomain_split",
        "indomain_reverse_split",
        "indomain_interval",
        "indomain_split_random",
        "outdomain_min",
        "outdomain_max",
        "outdomain_median",
        "outdomain_random",
    ]


class Model(minizinc.Model):
    def __init__(self):
        self.constants = []
        self.parameters = []
        self.variables = []
        self.constraints = []
        self.solve_criteria = None
        self.solve_expression = None
        self.solve_method = None
        self.restart_strategy = None
        self.solve_annotations = []
        self.model_mzn_str = None

        self.global_constraints = set()
        self.enums = {}
        self.function_declarations = []
        self.predicate_declarations = []

        self.last_solver = None
        self.last_solve_status = None
        self.last_solve_statistics = None
        self.last_solve_result = None
        self._compiled_model_text = None

        super().__init__()

    def set_solve_criteria(self, criteria: str, expr: Expression=None):
        self.solve_criteria = criteria
        self.solve_expression = expr

        if (criteria == SOLVE_MAXIMIZE or criteria == SOLVE_MINIMIZE):
            assert expr is not None
        elif (criteria == SOLVE_SATISFY):
            assert expr is None
        else:
            raise Exception(f"Invalid solve criteria: {criteria}")

    def set_solve_method(self, method: SearchAnnotation, restart_strategy: RestartStrategy=None):
        assert isinstance(method, (SeqSearch, SearchAnnotation))
        if (restart_strategy is not None):
            assert isinstance(restart_strategy, RestartStrategy)
        self.solve_method = method
        self.restart_strategy = restart_strategy

    def set_solve_annotations(self, annotations):
        self.solve_annotations = Expression._normalize_annotations(annotations, "annotations")

    def add_solve_annotation(self, annotation):
        self.solve_annotations.extend(Expression._normalize_annotations(annotation, "annotation"))

    def set_warm_start(self, variables, values):
        self.add_solve_annotation(Annotation("warm_start", list(variables), list(values)))

    def set_warm_start_array(self, warm_start_annotations):
        self.add_solve_annotation(Annotation("warm_start_array", list(warm_start_annotations)))

    def add_constant(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        constant = Constant(name, value, vtype)
        self.constants.append(constant)
        return constant

    def add_parameter(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        parameter = Parameter(name, value, vtype)
        self.parameters.append(parameter)
        return parameter

    def add_parameters(self, name: str, indices: List[Tuple[int]], values, vtype=Variable.VTYPE_INTEGER) -> ValueDict:
        if (isinstance(values, dict)):
            assert set(values.keys()) == set(indices)
            values_map = values
        elif (isinstance(values, list)):
            assert len(values) == len(indices)
            values_map = {idx: values[i] for i, idx in enumerate(indices)}
        else:
            values_map = {idx: values for idx in indices}

        parameters = ValueDict()
        for idx in indices:
            idx_str = str(idx).replace(", ", "_").replace("(", "").replace(")", "").replace("'", "").replace("-", "_")
            parameter = Parameter(f"{name}_{idx_str}", values_map[idx], vtype=vtype)
            self.parameters.append(parameter)
            parameters[idx] = parameter

        return parameters

    def add_enum(self, type_name: str, members: List[str]) -> EnumDomain:
        if (not isinstance(type_name, str) or not type_name.strip()):
            raise ValueError("Enum type name must be a non-empty string.")

        members = list(members)
        if (not len(members)):
            raise ValueError("Enum members must contain at least one value.")
        if (not all(isinstance(member, str) and member.strip() for member in members)):
            raise ValueError("Enum members must be non-empty strings.")
        if (len(set(members)) != len(members)):
            raise ValueError("Enum members must be unique.")

        enum_domain = EnumDomain(type_name, members)
        self.enums[type_name] = enum_domain
        return enum_domain

    def add_variable(self, name: str, vtype: int=Variable.VTYPE_INTEGER, val_min: int=None, val_max: int=None, domain: set=None, annotations=None):
        variable = Variable(name, vtype, val_min, val_max, domain, annotations=annotations)
        self.variables.append(variable)
        return variable
    
    def add_variables(self, name: str, indices: List[Tuple[int]], vtype: int=Variable.VTYPE_INTEGER, val_min: int=None, val_max: int=None, domains: set=None, annotations=None) -> ValueDict:

        # Domain
        if (domains is None):
            domains = {}
        elif (type(domains) is set):
            domains = {idx: domains for idx in indices}
        elif (type(domains) is list):
            assert len(domains) == len(indices)
            domains = {idx: domains[i] for i, idx in enumerate(indices)}
        elif (type(domains) is dict):
            assert len(domains) == len(indices)
            assert set(domains.keys()) == set(indices)
            domains = {idx: domains[idx] for idx in indices}

        # Annotations
        if (annotations is None):
            annotations = {}
        elif (isinstance(annotations, (str, Annotation))):
            annotations = {idx: [annotations] for idx in indices}
        elif (type(annotations) is list):
            assert len(annotations) == len(indices)
            annotations = {idx: annotations[i] for i, idx in enumerate(indices)}
        elif (type(annotations) is dict):
            assert set(annotations.keys()) == set(indices)
            annotations = {idx: annotations[idx] for idx in indices}

        variables = ValueDict()
        for idx in indices:
            idx_str = str(idx).replace(", ", "_").replace("(", "").replace(")", "").replace("'", "").replace("-", "_")
            variable = Variable(
                f"{name}_{idx_str}",
                vtype,
                val_min,
                val_max,
                domains.get(idx, None),
                annotations=annotations.get(idx, None),
            )
            self.variables.append(variable)
            variables[idx] = variable

        return variables

    def add_constraint(self, constraint: ExpressionBool, is_redundant=False):
        if (isinstance(constraint, Constraint)):
            constraint.is_redundant = is_redundant
            if (constraint.ctype != Constraint.CTYPE_NORMAL):
                self.global_constraints.add(constraint.ctype)

        elif (isinstance(constraint, ExpressionBool)):
            constraint = Constraint(constraint.name, is_redundant=is_redundant)

        else:
            raise Exception("invalid constraint type")

        self.constraints.append(constraint)
        return constraint

    def add_constraints(self, constraints: List[Constraint], is_redundant=False):
        constraints = list(constraints)
        assert all(isinstance(constraint, (Constraint, Expression, str, bool)) for constraint in constraints)
        for constraint in constraints:
            self.add_constraint(constraint, is_redundant=is_redundant)

    def add_function_declaration(self, declaration: str):
        assert isinstance(declaration, str)
        declaration = declaration.strip()
        assert len(declaration) > 0
        self.function_declarations.append(declaration.rstrip(";"))

    def add_predicate_declaration(self, declaration: str):
        assert isinstance(declaration, str)
        declaration = declaration.strip()
        assert len(declaration) > 0
        self.predicate_declarations.append(declaration.rstrip(";"))

    def call_function(self, name: str, *args, returns_bool: bool=False):
        return Expression.function(name, *args, returns_bool=returns_bool)

    def add_function_call(self, name: str, *args, is_redundant: bool=False):
        return self.add_constraint(self.call_function(name, *args, returns_bool=True), is_redundant=is_redundant)

    def call_predicate(self, name: str, *args) -> ExpressionBool:
        return Expression.predicate(name, *args)

    def add_predicate_call(self, name: str, *args, is_redundant: bool=False):
        return self.add_constraint(self.call_predicate(name, *args), is_redundant=is_redundant)

    def generate(self, debug=False):
        self._sync_compiled_model()
        if (debug):
            print(self.model_mzn_str)

    def _render_model_string(self) -> str:
        self.model_mzn_str = MznTextBackend().render_model(self.to_ir())
        return self.model_mzn_str

    def _sync_compiled_model(self) -> str:
        model_text = self._render_model_string()
        if (self._compiled_model_text != model_text):
            # Rebuild inherited minizinc.Model state to avoid hidden accumulation.
            super().__init__()
            self.add_string(model_text)
            self._compiled_model_text = model_text
        return model_text

    def _resolve_solver(self, solver: Union[str, Any]):
        if (isinstance(solver, str)):
            return minizinc.Solver.lookup(solver)
        return solver

    def _create_instance(self, config: SolverConfig):
        solver_obj = self._resolve_solver(config.solver)
        model_text = self._render_model_string()
        runtime_model = minizinc.Model()
        runtime_model.add_string(model_text)
        return minizinc.Instance(solver_obj, runtime_model), solver_obj

    def _normalize_solver_config(
        self,
        solver: Union[str, Any, SolverConfig, None]=None,
        timeout=None,
        random_seed: Optional[int]=None,
        threads: Optional[int]=None,
        free_search: bool=False,
        all_solutions: bool=False,
        **kwargs,
    ) -> SolverConfig:
        if (isinstance(solver, SolverConfig)):
            has_overrides = (
                timeout is not None
                or random_seed is not None
                or threads is not None
                or free_search is not False
                or all_solutions is not False
                or len(kwargs) > 0
            )
            if (has_overrides):
                raise ValueError("When passing SolverConfig to solve(), provide solve options only inside SolverConfig.")
            return solver

        return SolverConfig(
            solver="gecode" if (solver is None) else solver,
            timeout=timeout,
            random_seed=random_seed,
            threads=threads,
            free_search=free_search,
            all_solutions=all_solutions,
            extra_solve_args=dict(kwargs),
        )

    def _record_solve_outcome(self, solver_obj, result):
        self.last_solver = solver_obj
        self.last_solve_result = result
        self.last_solve_status = getattr(result, "status", None)
        self.last_solve_statistics = result.raw_statistics

    def get_last_solve_info(self) -> dict[str, Any]:
        return {
            "solver": self.last_solver,
            "status": self.last_solve_status,
            "statistics": self.last_solve_statistics,
            "result": self.last_solve_result,
        }

    def solve(
        self,
        solver: Union[str, Any, SolverConfig, None]=None,
        timeout=None,
        random_seed: Optional[int]=None,
        threads: Optional[int]=None,
        free_search: bool=False,
        all_solutions: bool=False,
        **kwargs,
    ):
        config = self._normalize_solver_config(
            solver=solver,
            timeout=timeout,
            random_seed=random_seed,
            threads=threads,
            free_search=free_search,
            all_solutions=all_solutions,
            **kwargs,
        )
        instance, solver_obj = self._create_instance(config=config)
        result = instance.solve(
            timeout=config.timeout,
            random_seed=config.random_seed,
            processes=config.threads,
            free_search=config.free_search,
            all_solutions=config.all_solutions,
            **config.extra_solve_args,
        )
        normalized = SolveResult(result)
        self._record_solve_outcome(solver_obj, normalized)
        return normalized

    def solve_with(self, config: SolverConfig):
        return self.solve(solver=config)

    def optimize(
        self,
        solver: Union[str, Any, SolverConfig, None]=None,
        timeout=None,
        random_seed: Optional[int]=None,
        threads: Optional[int]=None,
        free_search: bool=False,
        **kwargs,
    ):
        if (self.solve_criteria not in (SOLVE_MAXIMIZE, SOLVE_MINIMIZE)):
            raise ValueError("Model.optimize() requires solve criteria 'maximize' or 'minimize'.")

        return self.solve(
            solver=solver,
            timeout=timeout,
            random_seed=random_seed,
            threads=threads,
            free_search=free_search,
            all_solutions=False,
            **kwargs,
        )

    def check_satisfiable(
        self,
        solver: Union[str, Any, SolverConfig, None]=None,
        timeout=None,
        random_seed: Optional[int]=None,
        threads: Optional[int]=None,
        free_search: bool=False,
        **kwargs,
    ) -> bool:
        result = self.solve(
            solver=solver,
            timeout=timeout,
            random_seed=random_seed,
            threads=threads,
            free_search=free_search,
            all_solutions=False,
            **kwargs,
        )

        satisfiable_statuses = {
            minizinc.Status.SATISFIED,
            minizinc.Status.OPTIMAL_SOLUTION,
            minizinc.Status.ALL_SOLUTIONS,
            minizinc.Status.UNBOUNDED,
        }
        return result.status in satisfiable_statuses

    def to_ir(self) -> ModelIR:
        assert self.solve_criteria is not None

        includes = tuple(sorted(f"{gconst}.mzn" for gconst in self.global_constraints))

        constants_sorted = sorted(self.constants, key=lambda c: c.name)
        parameters_sorted = sorted(self.parameters, key=lambda p: p.name)
        variables_sorted = sorted(self.variables, key=lambda v: v.name)
        enum_declarations = tuple(
            self.enums[name].to_declaration()
            for name in sorted(self.enums.keys())
        )
        declarations = enum_declarations + tuple(
            line.rstrip("\n")
            for line in (a._to_mz() for a in constants_sorted + parameters_sorted + variables_sorted)
        )
        function_declarations = tuple(
            f"{line};" for line in sorted(set(self.function_declarations))
        )
        predicate_declarations = tuple(
            f"{line};" for line in sorted(set(self.predicate_declarations))
        )
        constraints = tuple(
            line.rstrip("\n")
            for line in (constraint._to_mz() for constraint in self.constraints)
        )
        solve = SolveIR(
            criteria=self.solve_criteria,
            expression=str(self.solve_expression) if (self.solve_expression is not None) else None,
            method=str(self.solve_method) if (self.solve_method is not None) else None,
            restart_strategy=str(self.restart_strategy) if (self.restart_strategy is not None) else None,
            annotations=tuple(self.solve_annotations),
        )
        return ModelIR(
            includes=includes,
            declarations=declarations,
            function_declarations=function_declarations,
            predicate_declarations=predicate_declarations,
            constraints=constraints,
            solve=solve,
        )

    def write(self, fn: str):
        if (self.model_mzn_str is None):
            self.generate()
        with open(fn, "w") as f:
            f.write(self.model_mzn_str)
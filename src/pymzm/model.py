
import minizinc
from typing import List, Tuple

from .exceptions import *
from .variable import *
from .constraint import *
from .expression import *
from .constant import *

SOLVE_MAXIMIZE = "maximize"
SOLVE_MINIMIZE = "minimize"
SOLVE_SATISFY = "satisfy"

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
    ]


class Model(minizinc.Model):
    def __init__(self):
        self.constants = []
        self.variables = []
        self.constraints = []
        self.solve_criteria = None
        self.solve_expression = None
        self.solve_method = None
        self.model_mzn_str = None

        self.global_constraints = set()

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

    def add_constant(self, name: str, value, vtype=Variable.VTYPE_INTEGER):
        constant = Constant(name, value, vtype)
        self.constants.append(constant)
        return constant

    def add_variable(self, name: str, vtype: int=Variable.VTYPE_INTEGER, val_min: int=None, val_max: int=None, domain: set=None):
        variable = Variable(name, vtype, val_min, val_max, domain)
        self.variables.append(variable)
        return variable
    
    def add_variables(self, name: str, indices: List[Tuple[int]], vtype: int=Variable.VTYPE_INTEGER, val_min: int=None, val_max: int=None, domains: set=None) -> ValueDict:

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

        variables = ValueDict()
        for idx in indices:
            idx_str = str(idx).replace(", ", "_").replace("(", "").replace(")", "").replace("'", "").replace("-", "_")
            variable = Variable(f"{name}_{idx_str}", vtype, val_min, val_max, domains.get(idx, None))
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

    def generate(self, debug=False):
        self.model_mzn_str = ""
        for gconst in self.global_constraints:
            self.model_mzn_str += f'include \"{gconst}.mzn\";\n'

        self.model_mzn_str += "".join(a._to_mz() for a in self.constants + self.variables + self.constraints)
        
        assert self.solve_criteria is not None
        _solve_method_str = ""
        if (self.solve_method is not None):
            _solve_method_str += f":: {self.solve_method}\n"
            
            if (self.restart_strategy is not None):
                _solve_method_str += f"      :: {self.restart_strategy}\n "

        _solve_method_str += f"{self.solve_criteria}"

        if (self.solve_expression is not None):
            _solve_method_str += f" {self.solve_expression}"
            
        self.model_mzn_str += f"solve {_solve_method_str};\n"

        self.add_string(self.model_mzn_str)
        if (debug):
            print(self.model_mzn_str)

    def write(self, fn: str):
        if (self.model_mzn_str is None):
            self.generate()
        with open(fn, "w") as f:
            f.write(self.model_mzn_str)
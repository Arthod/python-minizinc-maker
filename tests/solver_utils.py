import minizinc
import pymzm


DEFAULT_SOLVER_TAG = "gecode"
DEFAULT_RANDOM_SEED = 1
DEFAULT_THREADS = 1


def lookup_default_solver(tag: str = DEFAULT_SOLVER_TAG):
    return minizinc.Solver.lookup(tag)


def deterministic_solver_config(
    solver=DEFAULT_SOLVER_TAG,
    all_solutions: bool = False,
    timeout=None,
    random_seed: int = DEFAULT_RANDOM_SEED,
    threads: int = DEFAULT_THREADS,
    free_search: bool = False,
    **kwargs,
) -> pymzm.SolverConfig:
    return pymzm.SolverConfig(
        solver=solver,
        timeout=timeout,
        random_seed=random_seed,
        threads=threads,
        free_search=free_search,
        all_solutions=all_solutions,
        extra_solve_args=dict(kwargs),
    )


def deterministic_instance_solve(
    instance,
    all_solutions: bool = False,
    random_seed: int = DEFAULT_RANDOM_SEED,
    threads: int = DEFAULT_THREADS,
    free_search: bool = False,
    **kwargs,
):
    return instance.solve(
        all_solutions=all_solutions,
        random_seed=random_seed,
        processes=threads,
        free_search=free_search,
        **kwargs,
    )

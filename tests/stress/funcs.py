
import pymzm
import subprocess
import minizinc

def gen_model(cap, sizes):
    model = pymzm.Model()
    n = len(sizes)

    bin_loads = model.add_variables("bin_load", range(n), val_min=0, val_max=cap)
    model.add_constraint(pymzm.Constraint.decreasing(bin_loads))
    model.add_constraint(bin_loads[0] > 0)

    # Boolean if bin i has item j
    bin_items = model.add_variables("bin_item", [(i, j) for i in range(n) for j in range(n)], vtype=pymzm.Variable.VTYPE_BOOL)
    for i in range(len(bin_loads)):
        model.add_constraint(bin_loads[i] == pymzm.Expression.sum(bin_items[i, j] * sizes[j] for j in range(n)))
    for j in range(n):
        model.add_constraint(pymzm.Expression.sum(bin_items[i, j] for i in range(len(bin_loads))) == 1)

    # Solve
    model.set_solve_criteria(pymzm.SOLVE_MINIMIZE, pymzm.Expression.sum(bin_loads > 0))
    model.generate()
    model.write("py.mzn")
    return model

def compile_mzn_to_fzn(path, cap=None, n=None, stuff=None):
    if (cap is None):
        subprocess.run(f"minizinc -c {path}", stdout=subprocess.DEVNULL)
    else:
        data = f'\"cap={cap};n={n};stuff={stuff};\"'
        subprocess.run(f'minizinc -c --solver Gecode {path} -D {data}', stdout=subprocess.DEVNULL)


def solve_fzn(path):
    #minizinc -c tests/stress/model.mzn -D "cap=5" -D "n=5" -D "stuff=[3,3,3,3,3]"
    subprocess.run(f"minizinc {path}", stdout=subprocess.DEVNULL)
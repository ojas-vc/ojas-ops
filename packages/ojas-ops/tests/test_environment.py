"""Basic environment and dependency verification tests for Ojas Ops."""

import msgspec
import ojas_ops
import ortools
from ortools.sat.python import cp_model


class ResourceSpec(msgspec.Struct):
    id: str
    capacity: int = 1


def test_dependencies_and_version() -> None:
    assert ojas_ops.__version__ == "0.1.0"
    assert ortools.__version__ is not None
    assert msgspec.__version__ is not None


def test_msgspec_struct() -> None:
    res = ResourceSpec(id="machine-01", capacity=2)
    encoded = msgspec.json.encode(res)
    decoded = msgspec.json.decode(encoded, type=ResourceSpec)
    assert decoded.id == "machine-01"
    assert decoded.capacity == 2


def test_ortools_cp_sat_solver() -> None:
    model = cp_model.CpModel()
    x = model.new_int_var(0, 10, "x")
    y = model.new_int_var(0, 10, "y")
    model.add(x + 2 * y == 14)
    model.maximize(x + y)

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    assert status == cp_model.OPTIMAL
    assert solver.value(x) == 14 or (solver.value(x) + 2 * solver.value(y) == 14)
    assert solver.objective_value >= 7

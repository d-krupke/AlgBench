# a helper for getting the instances
from instances import TspLibGraphInstanceDb

# the solver we want to evaluate
from solver import GurobiTspSolver

# pip install algbench
from algbench import Benchmark


def run_solver_for_instance_name(instance_name: str, _instance):
    instance = _instance
    solver = GurobiTspSolver(instance)
    ub, lb = solver.solve(time_limit=30)
    return {
        "upper_bound": ub,
        "lower_bound": lb,
    }


if __name__ == "__main__":
    # A helper for managing the instances
    instances = TspLibGraphInstanceDb()
    # Download the instances if they are not already present
    instances.download()
    # Create a benchmark database
    benchmark = Benchmark("./my_results")
    # For every instance of size 0 to 500, run the solver
    for instance_name in instances.selection(0, 500):
        instance = instances[instance_name]
        # Tell the benchmark to run the solver for this instance
        # and store the results in the database. Only run the solver
        # if the results are not already present in the database.
        benchmark.add(
            run_solver_for_instance_name,
            instance_name=instance_name,
            _instance=instance,
        )
    # Compress the results to save significant disk space
    benchmark.compress()

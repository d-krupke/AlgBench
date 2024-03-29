# a helper for getting the instances
from instances import TspLibGraphInstanceDb

# the solver we want to evaluate
from solver import GurobiTspSolver

if __name__ == "__main__":
    # A helper for managing the instances
    instances = TspLibGraphInstanceDb()
    # Download the instances if they are not already present
    instances.download()
    # For every instance of size 0 to 500, run the solver
    for instance_name in instances.selection(0, 500):
        instance = instances[instance_name]
        solver = GurobiTspSolver(instance)
        ub, lb = solver.solve(time_limit=30)
        print(
            f"Instance {instance_name} solved with upper bound {ub} and lower bound {lb}."
        )

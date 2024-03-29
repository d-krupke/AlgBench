# pip install slurminade
import slurminade

# a helper for getting the instances
from instances import TspLibGraphInstanceDb

# the solver we want to evaluate
from solver import GurobiTspSolver

# pip install algbench
from algbench import Benchmark

# Create a benchmark database
benchmark = Benchmark("./my_results")
# A helper for managing the instances
instances = TspLibGraphInstanceDb()


def run_solver_for_instance_name(instance_name: str, _instance):
    instance = _instance
    solver = GurobiTspSolver(instance)
    ub, lb = solver.solve(time_limit=30)
    return {
        "upper_bound": ub,
        "lower_bound": lb,
    }


@slurminade.slurmify()
def run_solver_for_instance_name_on_slurm(instance_name: str):
    instance = instances[instance_name]
    benchmark.add(
        run_solver_for_instance_name,
        instance_name=instance_name,
        _instance=instance,
    )


@slurminade.node_setup
def configure_grb_license_path():
    # copy and paste solution for handling Gurobi licenses.
    import socket
    from pathlib import Path

    if "alg" not in socket.gethostname():
        return

    # TODO: Make sure that the license file is in the correct location
    # It is expected that the license file is in the following location:
    # ~/.gurobi/{$HOSTNAME}/gurobi.lic
    # You can of course change this path to whatever you like.
    grb_license_path = Path.home() / ".gurobi" / socket.gethostname() / "gurobi.lic"
    import os

    os.environ["GRB_LICENSE_FILE"] = str(grb_license_path)

    if not grb_license_path.exists():
        msg = "Gurobi License File does not exist."
        raise RuntimeError(msg)


@slurminade.slurmify(mail="ALL")
def compress_results():
    # Compress the results to save significant disk space
    benchmark.compress()


if __name__ == "__main__":
    slurminade.update_default_configuration(
        # Your supervisor will tell you these details
        partition="alg",  # Which partition to use. Usually group name.
        constraint="alggen05",  # Which workstations within the partition to use
        exclusive=True,  # To use all cores on a node exclusively
        mail_type="FAIL",  # Send mail on failure
        mail_user="krupke@ibr.cs.tu-bs.de",  # Mail to this address
    )

    # Download the instances if they are not already present
    instances.download()

    # For every instance of size 0 to 500, run the solver
    for instance_name in instances.selection(0, 500):
        run_solver_for_instance_name_on_slurm.distribute(instance_name)
    # Make sure that all further jobs are only started after all instances have been solved
    slurminade.join()
    # Compress the results to save significant disk space
    compress_results.distribute()

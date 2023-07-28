"""
This is a slightly modified version of `02_run_benchmark.py` that
uses slurminade to distribute the execution in a slurm environment.

This script will also work without a slurm environment.

THIS IS JUST FOR COMPARISON AND NOT AN ACTUAL PART OF THE EXAMPLE STUDY.
"""

import networkx as nx

# ---------------------
import slurminade
from _utils import InstanceDb

from algbench import Benchmark

# ---------------------

benchmark = Benchmark("03_benchmark_data")
instances = InstanceDb("./01_instances.zip")

# ---------------------
# this is just my slurm configuration, you would have to change it.
# Your admin will probably tell you what to insert here.
slurminade.update_default_configuration(
    partition="alg",
    constraint="alggen03",
    mail_user="my_mail@supermail.com",
    mail_type="ALL",  # or "FAIL" if you only want to be notified about failures.
)
slurminade.set_dispatch_limit(200)
# ----------------------


# ----------------------
# distribute the following function
@slurminade.slurmify()
# ----------------------
def load_instance_and_run(instance_name: str, alg_params):
    # load the instance outside the actual measurement
    g = instances[instance_name]

    def eval_greedy_alg(instance_name: str, alg_params, _instance: nx.Graph):
        # arguments starting with `_` are not saved.
        coloring = nx.coloring.greedy_coloring.greedy_color(_instance, **alg_params)
        return {  # the returned values are saved to the database
            "num_vertices": _instance.number_of_nodes(),
            "num_edges": _instance.number_of_edges(),
            "coloring": coloring,
            "n_colors": max(coloring.values()) + 1,
        }

    benchmark.add(eval_greedy_alg, instance_name, alg_params, g)


# --------------------------
# Compression is not thread-safe so we make it a separate function
# if you only notify about failures, you may want to do
# ``@slurminade.slurmify(mail_type="ALL)`` to be notified after completion.
@slurminade.slurmify()
def compress():
    benchmark.compress()


# --------------------------

alg_params_to_evaluate = [
    {"strategy": "largest_first", "interchange": True},
    {"strategy": "largest_first", "interchange": False},
    {"strategy": "random_sequential", "interchange": True},
    {"strategy": "random_sequential", "interchange": False},
    {"strategy": "smallest_last", "interchange": True},
    {"strategy": "smallest_last", "interchange": False},
    {"strategy": "independent_set"},
    {"strategy": "connected_sequential_bfs", "interchange": True},
    {"strategy": "connected_sequential_bfs", "interchange": False},
    {"strategy": "connected_sequential_dfs", "interchange": True},
    {"strategy": "connected_sequential_dfs", "interchange": False},
    {"strategy": "saturation_largest_first"},
]

if __name__ == "__main__":
    # ------------------------
    # tiny changes here
    with slurminade.Batch(100) as batch:  # combine up to 100 calls into into one task
        for instance_name in instances:
            for conf in alg_params_to_evaluate:
                load_instance_and_run.distribute(instance_name, conf)
        compress.wait_for(batch.flush()).distribute()  # after all runs finished
    # ----------------------

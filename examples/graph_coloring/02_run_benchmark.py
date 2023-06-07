"""
Run the actual benchmark.

You can run it multiple times, but it will only execute
the missing configurations. This does not save much time
here but when you have to deal with algorithms that
run for minutes, it is a life saver.
"""

import networkx as nx
from _utils import InstanceDb

from algbench import Benchmark

benchmark = Benchmark("03_benchmark_data")
instances = InstanceDb("./01_instances.zip")


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
    for instance_name in instances:
        print(instance_name)
        for conf in alg_params_to_evaluate:
            load_instance_and_run(instance_name, conf)
    benchmark.compress()
